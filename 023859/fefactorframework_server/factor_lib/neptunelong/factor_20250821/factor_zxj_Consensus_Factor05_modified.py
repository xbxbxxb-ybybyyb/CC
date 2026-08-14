import pandas as pd
import numpy as np
from itertools import chain
from sklearn.linear_model import LinearRegression
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_zxj_Consensus_Factor05_modified(BaseFactor):
    strategy_name = "neptunelong"
    factor_name = "zxj_Consensus_Factor05_modified"
    fill_na_value = 0 # 缺失值填充
    need_pre_calculate_T_N = True
    owner = "zxj"  # 开发人员姓名
    factor_explain = "AFR因子-回归填充" # 因子逻辑解释
    zcz_adjusted = "" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "" # 是否低耗时
    t_day_data = []
    #
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND',  # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 80,  # 注意为正数
         'column': ['turn', 'pct_chg','mkt_cap_ard']
         }]
    t_1_factor_data_types = ['MD']
    xdb_data = [
        {
       'name': 'xdb_researchreport_cs',
       'lag': 400 # 回看日期，N为往前回看1~N天
    }]
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            def f_calc_std(factor_series):
                return np.std(factor_series[~np.isnan(factor_series)], ddof=1)

            def calculate_afr_final_corrected_optimized(df: pd.DataFrame) -> pd.DataFrame:
                
                # 原始索引用于最后的结果对齐
                original_index = df.index.to_frame(index=False).drop_duplicates()
                
                processed_df = df.reset_index()

                if processed_df['dt'].nunique() != 1:
                    raise ValueError("输入DataFrame的'dt'索引应只包含一个唯一日期。")
                current_dt = processed_df['dt'].iloc[0]

                # ===== 动态计算FY1和FY2年份 (逻辑不变) =====
                current_year = current_dt.year
                cutoff_date = pd.to_datetime(f'{current_year}-04-30')
                
                if current_dt <= cutoff_date:
                    target_fy1_year = current_year
                    target_fy2_year = current_year + 1
                else:
                    target_fy1_year = current_year + 1
                    target_fy2_year = current_year + 2
                    
                print(f"当前日期 {current_dt.date()}，目标FY1年份为: {target_fy1_year}")
                
                # ===== 核心优化: 向量化实现 explode 功能 =====
                # 步骤 1.1: 拆分AUTHOR字段
                processed_df['AUTHOR'] = processed_df['AUTHOR'].fillna('').astype(str).str.strip().str.split(',')
                
                # 步骤 1.2: 计算每行需要重复的次数 (即作者数量)
                author_counts = processed_df['AUTHOR'].map(len) # .str.len() 也可以
                
                # 步骤 1.3: 使用 np.repeat 高效复制行
                expanded_df = processed_df.loc[np.repeat(processed_df.index, author_counts)].copy()
                
                # 步骤 1.4: "压平"作者列表并赋值
                expanded_df['AUTHOR'] = list(chain.from_iterable(processed_df['AUTHOR']))
                
                # 过滤掉AUTHOR为空字符串的行
                expanded_df = expanded_df[expanded_df['AUTHOR'].str.strip() != ''].copy()
                processed_df = expanded_df

                # 如果展开后没有数据，直接返回
                if processed_df.empty:
                    final_df = original_index.copy()
                    final_df['AFR'] = np.nan
                    return final_df.set_index(['dt', 'Ticker'])
                    
                # ===== 辅助优化: 使用Category类型 =====
                processed_df['SECUCODE'] = processed_df['SECUCODE'].astype('category')
                processed_df['AUTHOR'] = processed_df['AUTHOR'].astype('category')
                processed_df['Ticker'] = processed_df['Ticker'].astype('category')
                
                # 步骤2: 数据类型转换和排序 (逻辑不变)
                processed_df['WRITINGDATE'] = pd.to_datetime(processed_df['WRITINGDATE'], errors='coerce')
                processed_df['FORECASTYEAR'] = pd.to_numeric(processed_df['FORECASTYEAR'], errors='coerce')
                processed_df['FORECASTNP'] = pd.to_numeric(processed_df['FORECASTNP'], errors='coerce')
                processed_df.dropna(subset=['WRITINGDATE', 'FORECASTYEAR', 'FORECASTNP'], inplace=True)
                
                processed_df.sort_values(by=['SECUCODE', 'AUTHOR', 'FORECASTYEAR', 'WRITINGDATE'], inplace=True)

                # 步骤3: 计算个体分析师的预期调整幅度 (逻辑不变)
                # 这一步需要用到全部历史数据来正确配对，因此不能提前过滤
                grouped = processed_df.groupby(['SECUCODE', 'AUTHOR', 'FORECASTYEAR'])
                processed_df['PREVIOUS_FORECASTNP'] = grouped['FORECASTNP'].shift(1)
                
                valid_adjustments = processed_df[processed_df['PREVIOUS_FORECASTNP'].notna() & (processed_df['PREVIOUS_FORECASTNP'] > 0)].copy()
                valid_adjustments['ADJUSTMENT'] = (valid_adjustments['FORECASTNP'] / valid_adjustments['PREVIOUS_FORECASTNP']) - 1

                # 步骤4: 根据研报规则进行过滤和聚合 (逻辑不变)
                # ===== 逻辑修正：在此处进行时间窗口过滤 =====
                # 这里的过滤是基于新研报的 `WRITINGDATE`，与原始逻辑完全一致
                time_window = current_dt - pd.Timedelta(days=90)
                recent_adjustments = valid_adjustments[valid_adjustments['WRITINGDATE'] >= time_window].copy()

                # 报告数量的计算逻辑保持不变，基于原始df进行
                report_counts = df.reset_index().drop_duplicates(subset=['REPORTID', 'Ticker'])
                report_counts['WRITINGDATE'] = pd.to_datetime(report_counts['WRITINGDATE'], errors='coerce')
                recent_report_counts = report_counts[report_counts['WRITINGDATE'] >= time_window]
                ticker_counts = recent_report_counts.groupby('Ticker').size()
                valid_tickers = ticker_counts[ticker_counts >= 3].index
                
                final_data = recent_adjustments[recent_adjustments['Ticker'].isin(valid_tickers)].copy()
                final_data['ADJUSTMENT'] = final_data['ADJUSTMENT'].clip(-0.25, 0.25)
                
                # 使用动态计算出的 target_fy1_year 进行过滤
                afr_result = final_data[final_data['FORECASTYEAR'] == target_fy1_year].groupby(['dt', 'Ticker'])['ADJUSTMENT'].mean()
                
                # 步骤5: 格式化输出 (逻辑不变)
                afr_df = afr_result.to_frame(name='AFR')
                
                final_df = pd.merge(original_index, afr_df, on=['dt', 'Ticker'], how='left')
                final_df.set_index(['dt', 'Ticker'], inplace=True)
                
                return final_df
            
            def calculate_regression_features(market_data_df: pd.DataFrame) -> pd.DataFrame:
                """
                根据输入的量价数据计算用于回归填充的自变量。

                Args:
                    market_data_df (pd.DataFrame): 
                        一个以 [dt, Ticker] 为 MultiIndex 的 DataFrame，
                        必须包含 'mkt_cap_and', 'turn', 和 'pct_chg' 列。

                Returns:
                    pd.DataFrame: 
                        一个以 [dt, Ticker] 为 MultiIndex 的新 DataFrame，
                        包含计算出的四个特征列：'ln_mkt_cap', 'avg_turn_20d', 
                        'volatility_20d', 'momentum_20d'。
                        滚动窗口计算会产生NaN值（例如，每个股票的前19个数据点）。
                """
                # 确保输入为DataFrame
                if not isinstance(market_data_df, pd.DataFrame):
                    raise TypeError("输入的数据必须是 pandas DataFrame。")

                # 定义滚动窗口大小
                ROLLING_WINDOW = 20
                
                # 创建一个副本以避免修改原始数据
                data = market_data_df.copy()

                # 1. 计算对数总市值 (ln_mkt_cap)
                # 这是一个逐元素操作，不需要分组
                features_df = pd.DataFrame(index=data.index)
                features_df['ln_mkt_cap'] = np.log(data['mkt_cap_ard'])

                # 按 'Ticker' 分组以进行滚动计算
                grouped_by_ticker = data.groupby('Ticker')

                # 2. 计算月均换手率 (avg_turn_20d)
                avg_turn = grouped_by_ticker['turn'].rolling(
                    window=ROLLING_WINDOW
                ).mean()
                
                # 3. 计算历史波动率 (volatility_20d)
                volatility = grouped_by_ticker['pct_chg'].rolling(
                    window=ROLLING_WINDOW
                ).apply(f_calc_std)

                # 4. 计算中期动量 (momentum_20d)
                # 首先，将百分比收益转换为收益因子 (1 + r)
                data['return_factor'] = 1 + data['pct_chg'] / 100
                # 计算滚动累乘积，然后减1得到累计收益率
                momentum = data.groupby('Ticker')['return_factor'].rolling(
                    window=ROLLING_WINDOW
                ).apply(np.prod, raw=True).droplevel(0) - 1


                # 将计算结果合并到features_df中
                # rolling操作后索引会变为三层，需要去除分组的索引层
                features_df['avg_turn_20d'] = avg_turn.droplevel(0)
                features_df['volatility_20d'] = volatility.droplevel(0)
                features_df['momentum_20d'] = momentum
                
                return features_df

            def impute_missing_factor_with_lagged_features(
                factor_df: pd.DataFrame,
                features_df: pd.DataFrame
            ) -> pd.DataFrame:
                
                # --- 1. 数据准备和对齐 ---
                imputed_factor_df = factor_df.copy()

                if imputed_factor_df.index.get_level_values('dt').nunique() != 1:
                    raise ValueError("factor_df 必须只包含一个最新日期的数据。")

                if features_df.empty:
                    print("警告：特征 DataFrame (features_df) 为空，无法进行填充。")
                    return imputed_factor_df

                t_minus_1_date = features_df.index.get_level_values('dt').max()

                features_t_minus_1 = features_df.loc[
                    features_df.index.get_level_values('dt') == t_minus_1_date
                ]

                # 将 T 日的因子和 T-1 日的特征按 Ticker 合并
                merged_df = pd.merge(
                    imputed_factor_df.reset_index(),
                    # --- THIS IS THE CORRECTED LINE ---
                    features_t_minus_1.reset_index().drop(columns=['dt']),
                    on='Ticker',
                    how='left'
                )

                # --- 2. 划分训练集和待填充集 ---
                merged_df.dropna(subset=features_t_minus_1.columns, inplace=True)
                train_set = merged_df[merged_df['AFR'].notna()]
                impute_set = merged_df[merged_df['AFR'].isna()]

                if impute_set.empty:
                    print("没有需要填充的缺失值。")
                    return imputed_factor_df

                if train_set.empty:
                    print("警告：没有可用的训练数据来训练回归模型。")
                    return imputed_factor_df

                # --- 3. 模型训练与预测 ---
                feature_columns = features_t_minus_1.columns
                X_train = train_set[feature_columns]
                y_train = train_set['AFR']

                model = LinearRegression()
                model.fit(X_train, y_train)

                X_impute = impute_set[feature_columns]
                predicted_AFR = model.predict(X_impute)

                # --- 4. 填充结果并返回 ---
                impute_indices = pd.MultiIndex.from_frame(impute_set[['dt', 'Ticker']])
                imputed_factor_df.loc[impute_indices, 'AFR'] = predicted_AFR

                return imputed_factor_df
    
# -------------------------------------------------------------------------------------------------------------------
            daily_df = database['xdb_researchreport_cs']
            df_md = database['MD_CHINA_STOCK_DAILY_WIND']
            factor_df = calculate_afr_final_corrected_optimized(daily_df)
            features_df = calculate_regression_features(df_md)
            factors_df_filled = impute_missing_factor_with_lagged_features(factor_df,features_df)
            factors_df_filled.rename(columns={'AFR': self.factor_name},inplace=True)
            database['pre_T_N'] = factors_df_filled[[self.factor_name]] # cs要返回df

            return database
        
    def prepare_T_data(self, database):
        # 如果加载数据阶段出现某些T日高频数据或者xdb数据缺失，则跳过该日计算
        if database["skip"] == True:
            return database
        else:
            return database

    def calculate(self, database):
        if database["skip"] == True:  # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            res = database['pre_T_N']
            # ---------------------------------------------------------------------------------------------------------------
            return res
