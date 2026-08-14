import pandas as pd
import numpy as np
from itertools import chain
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_zxj_Consensus_Factor05(BaseFactor):
    strategy_name = "neptune"
    factor_name = "zxj_Consensus_Factor05"
    fill_na_value = 0 # 缺失值填充
    need_pre_calculate_T_N = True
    owner = "zxj"  # 开发人员姓名
    factor_explain = "AFR因子" # 因子逻辑解释
    zcz_adjusted = "" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "" # 是否低耗时：是/否
    #
    t_day_data = []
    xdb_data = [
        {
        'name':'xdb_researchreport_cs',
        'lag':700
        }
    ]
    t_1_factor_data = []  # T-N factor数据，格式如上
    t_1_factor_data_types = [] # T-1的h5文件类型列表
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:

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
# -------------------------------------------------------------------------------------------------------------------
            daily_df = database['xdb_researchreport_cs']
            factor_df = calculate_afr_final_corrected_optimized(daily_df)
            factor_df.rename(columns={'AFR': self.factor_name},inplace=True)
            database['pre_T_N'] = factor_df[[self.factor_name]] # cs要返回df

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
