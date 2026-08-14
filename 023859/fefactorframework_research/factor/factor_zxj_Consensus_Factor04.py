import pandas as pd
import numpy as np
from typing import Dict, List
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_zxj_Consensus_Factor04(BaseFactor):
    strategy_name = "neptune"
    factor_name = "zxj_Consensus_Factor04"
    fill_na_value = 0 # 缺失值填充
    need_pre_calculate_T_N = True
    owner = "zxj"  # 开发人员姓名
    factor_explain = "东方证券FOM因子" # 因子逻辑解释
    zcz_adjusted = "" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "" # 是否低耗时：是/否
    #
    t_day_data = []
    xdb_data = [
        {
        'name':'xdb_researchreport_cs',
        'lag':400
        }
    ]
    t_1_factor_data = []  # T-N factor数据，格式如上
    t_1_factor_data_types = [] # T-1的h5文件类型列表
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
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

            daily_df = database['xdb_researchreport_cs']
            factor_df = calculate_fom_optimized(daily_df)
            factor_df.rename(columns={'FOM': self.factor_name},inplace=True)
            # -------------------------------------------------------------------------------------------------------------------
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
