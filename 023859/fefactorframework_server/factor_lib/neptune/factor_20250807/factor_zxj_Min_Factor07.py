import pandas as pd
import numpy as np
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_zxj_Min_Factor07(BaseFactor):
    strategy_name = "neptune"
    factor_name = "zxj_Min_Factor07"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "zxj"
    factor_explain = "高阶矩因子"
    zcz_adjusted = "否"
    logic_type = ""
    low_cost = ""
    t_day_data = []

    xdb_data = [
        {
        'name': 'xdb_tick1m_cs', 
        'lag': 1,
    }]

    def pre_calculate_T_N_data(self, database):
        if database.get("skip", False):
            return database

        def calculate_factors(log_returns: np.ndarray) -> dict:
            n = len(log_returns)
            if n < 2:
                return {
                    'RV': np.nan, 'RS': np.nan, 'RK': np.nan, 
                    'RHS': np.nan, 'RHT': np.nan
                }

            # 已实现方差 (Realized Variance)
            rv = np.sum(log_returns**2)
            
            if rv == 0: # 如果波动为0，所有高阶矩都为NaN
                return {
                    'RV': rv, 'RS': np.nan, 'RK': np.nan, 
                    'RHS': np.nan, 'RHT': np.nan
                }

            # 已实现偏度 (Realized Skewness)
            rs = np.sqrt(n) * np.sum(log_returns**3) / (rv**(3/2))

            # 已实现峰度 (Realized Kurtosis)
            rk = n * np.sum(log_returns**4) / (rv**2)
            
            # 已实现超偏度 (Realized Hyper-skewness)
            rhs = (n**(3/2)) * np.sum(log_returns**5) / (rv**(5/2))

            # 已实现超尾度 (Realized Hyper-tailedness)
            rht = (n**2) * np.sum(log_returns**6) / (rv**3)

            return {'RV': rv, 'RS': rs, 'RK': rk, 'RHS': rhs, 'RHT': rht}


        def process_daily_data(daily_df: pd.DataFrame, current_date: pd.Timestamp) -> pd.DataFrame:
            """
            处理已加载的单日高频数据DataFrame，计算每只股票的因子值。

            参数:
            daily_df (pd.DataFrame): 已加载的、包含当日所有股票高频数据的DataFrame。
                                    假设其索引为 (dt, Ticker) 的 MultiIndex。
            current_date (pd.Timestamp): 当前处理的日期。

            返回:
            pd.DataFrame: 包含当日所有股票因子值的DataFrame。
            """
            
            # 因为传入的DataFrame已经是MultiIndex，我们直接按level='Ticker'分组
            # 如果不是MultiIndex，则使用 daily_df.groupby('Ticker')
            if isinstance(daily_df.index, pd.MultiIndex):
                grouped = daily_df.groupby(level='Ticker')
            else:
                # 兼容非MultiIndex的输入
                if 'Ticker' not in daily_df.columns:
                    daily_df['Ticker'] = daily_df.index.get_level_values('Ticker')
                grouped = daily_df.groupby('Ticker')


            daily_results = []

            for ticker, stock_data in grouped:
                # 排序以确保时间序列正确
                stock_data = stock_data.sort_values('MDTime')
                
                # 转换并过滤掉价格为0或NaN的数据
                prices = pd.to_numeric(stock_data['LastPx'], errors='coerce')
                prices = prices[prices > 0].dropna()
                
                if len(prices) < 10: # 如果有效数据点太少，则跳过
                    continue

                all_factors = []
                # 下采样过程
                for i in range(5):
                    sub_sampled_prices = prices.iloc[i::5]
                    if len(sub_sampled_prices) < 2:
                        continue
                    
                    # 计算对数收益率
                    log_returns = np.log(sub_sampled_prices).diff().dropna().values
                    
                    if len(log_returns) > 0:
                        factors = calculate_factors(log_returns)
                        all_factors.append(factors)
                
                if not all_factors:
                    continue
                    
                # 对5组下采样结果取平均
                avg_factors = pd.DataFrame(all_factors).mean().to_dict()
                avg_factors['Ticker'] = ticker
                daily_results.append(avg_factors)

            if not daily_results:
                return pd.DataFrame()

            result_df = pd.DataFrame(daily_results)
            result_df['dt'] = current_date
            
            return result_df

        daily_data = database['xdb_tick1m_cs']
        current_date = daily_data.index[0][0]
        final_factors_df = process_daily_data(daily_data,current_date)

        final_factors_df = final_factors_df.set_index(['dt', 'Ticker'])
        final_factors_df = final_factors_df.rename(columns={
            'RS': 'subRS_5min_day',
            'RK': 'subRK_5min_day',
            'RHS': 'subRHS_5min_day',
            'RHT': 'subRHT_5min_day'
        })

        final_factors_df = final_factors_df[['subRS_5min_day', 'subRK_5min_day', 'subRHS_5min_day', 'subRHT_5min_day']]
        final_factors_df.rename(columns={'subRHS_5min_day': self.factor_name }, inplace=True) 
        database['pre_T_N'] = final_factors_df[[self.factor_name]]
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