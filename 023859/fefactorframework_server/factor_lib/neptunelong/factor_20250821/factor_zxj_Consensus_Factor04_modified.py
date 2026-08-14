import pandas as pd
import numpy as np
from typing import Dict, List
from sklearn.linear_model import LinearRegression
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_zxj_Consensus_Factor04_modified(BaseFactor):
    strategy_name = "neptunelong"
    factor_name = "zxj_Consensus_Factor04_modified"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "zxj"  # 开发人员姓名
    factor_explain = "东方证券FOM因子-回归填充" # 因子逻辑解释
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
            
            def calculate_fom_optimized(df: pd.DataFrame) -> pd.DataFrame:
                
                df_copy = df.reset_index()

                # 检查必要的列是否存在
                required_cols = ['dt', 'Ticker', 'WRITINGDATE', 'FORECASTYEAR', 'FORECASTQUARTER', 'FORECASTNP']
                if not all(col in df_copy.columns for col in required_cols):
                    raise ValueError(f"输入DataFrame必须包含以下列，且大小写需匹配: {required_cols}")

                # 获取唯一的计算日期
                single_dt = pd.to_datetime(df_copy['dt'].iloc[0])
                
                # 转换WRITINGDATE列为日期格式
                df_copy['WRITINGDATE'] = pd.to_datetime(df_copy['WRITINGDATE'], errors='coerce')
                df_copy.dropna(subset=['WRITINGDATE'], inplace=True)

                def _calculate_fom_for_snapshot(ticker_group: pd.DataFrame) -> float:
                    """
                    对单个Ticker的所有历史报告，计算其在指定快照日(single_dt)的FOM值。
                    """
                    # 确定回溯期：从快照日往前12个月
                    lookback_start_date = single_dt - pd.DateOffset(months=12)
                    
                    # 筛选出在回溯期内发布的所有报告
                    reports_in_window = ticker_group[
                        (ticker_group['WRITINGDATE'] >= lookback_start_date) &
                        (ticker_group['WRITINGDATE'] <= single_dt)
                    ]
                    
                    # 确定预测目标年份：每年4月30日为切换时点
                    if single_dt.month < 4 or (single_dt.month == 4 and single_dt.day < 30):
                        target_year = single_dt.year - 1
                    else:
                        target_year = single_dt.year
                    
                    # 筛选出针对目标年份的年度预测报告
                    final_reports = reports_in_window[
                        (reports_in_window['FORECASTYEAR'] == target_year) &
                        (reports_in_window['FORECASTQUARTER'] == 4)
                    ]
                    
                    # 研报要求至少有3篇报告，否则因子值为空
                    if len(final_reports) < 3:
                        return np.nan
                    
                    # 确定基准预测值：取最新报告的预测净利润
                    latest_writing_date = final_reports['WRITINGDATE'].max()
                    benchmarks = final_reports[final_reports['WRITINGDATE'] == latest_writing_date]['FORECASTNP']
                    
                    if benchmarks.empty:
                        return np.nan

                    fom_values: List[float] = []
                    N = len(final_reports)
                    all_forecasts = final_reports['FORECASTNP']
                    
                    # 如果同一天有多篇最新报告，分别计算FOM后取平均值
                    for p_latest in benchmarks:
                        K = (all_forecasts < p_latest).sum()
                        M = (all_forecasts > p_latest).sum()
                        fom = (K - M) / N
                        fom_values.append(fom)
                    
                    return np.mean(fom_values) if fom_values else np.nan

                # --- 2. 分组计算 ---
                # 按Ticker分组，对每个组应用计算函数
                fom_series = df_copy.groupby('Ticker').apply(_calculate_fom_for_snapshot)
                
                # --- 3. 格式化输出 ---
                fom_df = fom_series.to_frame(name='FOM')
                #fom_df.dropna(inplace=True)
                
                fom_df['dt'] = single_dt
                
                # 设置最终的MultiIndex并排序
                fom_df = fom_df.reset_index().set_index(['dt', 'Ticker']).sort_index()
                
                return fom_df
            
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
                """
                使用前一天的特征数据，通过回归模型填充最新一天因子数据中的缺失值。
                T-1日的数据会自动从features_df中取最新的一天。

                Args:
                    factor_df (pd.DataFrame):
                        一个以 [dt, Ticker] 为 MultiIndex 的 DataFrame，只包含最新一天 (T) 的数据。
                        其中包含名为 'FOM' 的因子列，部分值可能为 NaN。
                    features_df (pd.DataFrame):
                        一个以 [dt, Ticker] 为 MultiIndex 的 DataFrame，包含历史特征数据。
                        此函数将使用其中最新的日期作为 T-1 日的数据。

                Returns:
                    pd.DataFrame:
                        一个新的 DataFrame，格式与输入的 factor_df 相同，但 'FOM' 列中的
                        NaN 值已被回归模型的预测值填充。
                """
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
                train_set = merged_df[merged_df['FOM'].notna()]
                impute_set = merged_df[merged_df['FOM'].isna()]

                if impute_set.empty:
                    print("没有需要填充的缺失值。")
                    return imputed_factor_df

                if train_set.empty:
                    print("警告：没有可用的训练数据来训练回归模型。")
                    return imputed_factor_df

                # --- 3. 模型训练与预测 ---
                feature_columns = features_t_minus_1.columns
                X_train = train_set[feature_columns]
                y_train = train_set['FOM']

                model = LinearRegression()
                model.fit(X_train, y_train)

                X_impute = impute_set[feature_columns]
                predicted_fom = model.predict(X_impute)

                # --- 4. 填充结果并返回 ---
                impute_indices = pd.MultiIndex.from_frame(impute_set[['dt', 'Ticker']])
                imputed_factor_df.loc[impute_indices, 'FOM'] = predicted_fom

                return imputed_factor_df

            daily_df = database['xdb_researchreport_cs']
            df_md = database['MD_CHINA_STOCK_DAILY_WIND']
            factor_df = calculate_fom_optimized(daily_df)
            features_df = calculate_regression_features(df_md)
            factors_df_filled = impute_missing_factor_with_lagged_features(factor_df,features_df)
            factors_df_filled.rename(columns={'FOM': self.factor_name},inplace=True)
            # -------------------------------------------------------------------------------------------------------------------
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
        

