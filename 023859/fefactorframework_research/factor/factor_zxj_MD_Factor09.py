import pandas as pd
import numpy as np
from numpy.lib.stride_tricks import as_strided
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_zxj_MD_Factor09(BaseFactor):
    strategy_name = "neptune"
    factor_name = "zxj_MD_Factor09"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "zxj"  # 开发人员姓名
    factor_explain = "历史相似波动率"
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "" # 是否低耗时
    #
    t_day_data = []
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND',
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 200,
         'column': ['high', 'low', 'close','pre_close', 'pct_chg','adjfactor']
    }]
    t_1_factor_data_types = ['MD']

    def pre_calculate_T_N_data(self, database):
        if database.get("skip", False):
            return database
        else:

            df_MD = database['MD_CHINA_STOCK_DAILY_WIND']
            current_date =df_MD.index.get_level_values('dt').unique()[-1]
            
            factor_params = {
                'RW_r': 6, 'HW_r': 120, 'H_r': 6, 'Threshold_r': 0.40, 'Holding_Time_r': 5,
                'RW_v': 5, 'HW_v': 20, 'Threshold_v': 0.40, 'Holding_Time_v': 4,
            }

            def calculate_factors_for_stock_optimized(stock_data, params):
               
                # 解包参数
                RW_r, HW_r, H_r, Threshold_r, Holding_Time_r = (
                    params['RW_r'], params['HW_r'], params['H_r'],
                    params['Threshold_r'], params['Holding_Time_r']
                )
                RW_v, HW_v, Threshold_v, Holding_Time_v = (
                    params['RW_v'], params['HW_v'],
                    params['Threshold_v'], params['Holding_Time_v']
                )

                adj_close = stock_data['adj_close'].values
                excess_returns = stock_data['excess_return'].values
                n_days = len(adj_close)

                # --- 辅助函数：向量化计算相关系数 ---
                def vectorized_correlation(x, y_matrix):
                    if x.size == 0 or y_matrix.size == 0: return np.array([])
                    x_std_val = np.std(x)
                    if x_std_val < 1e-9: return np.full(y_matrix.shape[0], np.nan)
                    
                    x_std = (x - np.mean(x)) / x_std_val
                    
                    y_mean = np.mean(y_matrix, axis=1, keepdims=True)
                    y_std = np.std(y_matrix, axis=1, keepdims=True)
                    
                    # 避免除以零
                    y_std[y_std < 1e-9] = 1.0 
                    
                    y_matrix_std = (y_matrix - y_mean) / y_std
                    
                    corr = np.dot(y_matrix_std, x_std) / len(x)
                    return corr

                similar_reverse_factor = np.nan
                count_r = 0
                if n_days >= RW_r + HW_r:
                    current_sequence_r = adj_close[-RW_r:]
                    
                    if not (np.isnan(current_sequence_r).any() or np.std(current_sequence_r) < 1e-8):
                       
                        search_block_start_idx = n_days - HW_r - RW_r
                        search_block_end_idx = n_days - RW_r
                        search_data_r = adj_close[search_block_start_idx:search_block_end_idx]

                        num_windows_r = HW_r - RW_r + 1
                        shape = (num_windows_r, RW_r)
                        strides = (search_data_r.strides[0], search_data_r.strides[0])
                        history_windows_r = as_strided(search_data_r, shape=shape, strides=strides)
                        
                        correlations_r = vectorized_correlation(current_sequence_r, history_windows_r)
                        
                        # 向量化筛选并计数
                        valid_indices = np.where(np.abs(correlations_r) >= Threshold_r)[0]
                        count_r = len(valid_indices)

                        if count_r >= 2:
                            # 计算未来收益的起始索引 (基于原始数组 adj_close 的位置)
                            # 这些索引对应于每个匹配到的历史窗口之后的位置
                            return_start_indices = search_block_start_idx + valid_indices + RW_r
                            
                            future_return_indices = return_start_indices[:, None] + np.arange(Holding_Time_r)

                            if future_return_indices.size > 0 and future_return_indices[-1, -1] < n_days:
                                future_returns_matrix = excess_returns[future_return_indices]
                                cumulative_returns = np.nanprod(1 + future_returns_matrix, axis=1) - 1
                                signed_returns = cumulative_returns * np.sign(correlations_r[valid_indices])
                                
                                n = count_r
                                decay_lambda = np.log(2) / H_r
                                k = np.arange(1, n + 1)
                                weights = np.exp(decay_lambda * k)
                                weights /= np.sum(weights)
                                weighted_avg_return = np.sum(signed_returns * weights)
                                similar_reverse_factor = -weighted_avg_return

                similar_low_vol_factor = np.nan
                count_v = 0
                if n_days >= RW_v + HW_v:
                    current_sequence_v = adj_close[-RW_v:]
                    
                    if not (np.isnan(current_sequence_v).any() or np.std(current_sequence_v) < 1e-8):
                        
                        search_block_start_idx_v = n_days - HW_v - RW_v
                        search_block_end_idx_v = n_days - RW_v
                        search_data_v = adj_close[search_block_start_idx_v:search_block_end_idx_v]

                        num_windows_v = HW_v - RW_v + 1
                        shape_v = (num_windows_v, RW_v)
                        strides_v = (search_data_v.strides[0], search_data_v.strides[0])
                        history_windows_v = as_strided(search_data_v, shape=shape_v, strides=strides_v)
                        
                        correlations_v = vectorized_correlation(current_sequence_v, history_windows_v)
                        valid_indices_v = np.where(np.abs(correlations_v) >= Threshold_v)[0]
                        count_v = len(valid_indices_v)

                        if count_v >= 2:
                            return_start_indices_v = search_block_start_idx_v + valid_indices_v + RW_v
                            future_return_indices_v = return_start_indices_v[:, None] + np.arange(Holding_Time_v)
                            
                            if future_return_indices_v.size > 0 and future_return_indices_v[-1, -1] < n_days:
                                future_returns_matrix_v = excess_returns[future_return_indices_v]
                                cumulative_returns_v = np.nanprod(1 + future_returns_matrix_v, axis=1) - 1
                                
                                std_dev = np.std(cumulative_returns_v, ddof=1)
                                if std_dev > 1e-9:
                                    similar_low_vol_factor = 1 / std_dev
                                    
                return similar_reverse_factor, similar_low_vol_factor, int(count_r), int(count_v)
            
            def calculate_factors_for_day_optimized(current_date, df_full_history, params):
               
                results = df_full_history.groupby('Ticker').apply(calculate_factors_for_stock_optimized, params=params)
                
                if results.empty: return pd.DataFrame()
                
                results_df = pd.DataFrame(
                    results.tolist(), 
                    index=results.index, 
                    columns=['Similar_Reverse', 'Similar_Low_Volatility', 'Count_Reverse', 'Count_Low_Volatility']
                )
                results_df['dt'] = current_date
                results_df = results_df.reset_index().set_index(['dt', 'Ticker'])
                results_df[['Count_Reverse', 'Count_Low_Volatility']] = results_df[['Count_Reverse', 'Count_Low_Volatility']].astype(int)
                return results_df

            df_MD['adj_close'] = df_MD['close'] * df_MD['adjfactor']
            market_return_daily = df_MD.groupby('dt')['pct_chg'].mean()
            df_MD = df_MD.join(market_return_daily.rename('market_return'), on='dt')
            df_MD['excess_return'] = (df_MD['pct_chg'] - df_MD['market_return']) / 100

            # 计算所需的最大历史数据长度
            max_history_days_r = factor_params['RW_r'] + factor_params['HW_r']
            max_history_days_v = factor_params['RW_v'] + factor_params['HW_v']
            # 我们需要的天数是历史窗口+当前窗口
            max_history_len = max(max_history_days_r, max_history_days_v) + 1

            unique_dates = df_MD.index.get_level_values('dt').unique().sort_values()
            date_iloc = unique_dates.get_loc(current_date)
            # 确定历史数据的起始日期
            history_start_iloc = date_iloc - max_history_len
            history_start_date = unique_dates[history_start_iloc]
            
            # 切片数据：从历史起点到当前日期
            df_slice = df_MD.loc[(df_MD.index.get_level_values('dt') >= history_start_date) &
                                (df_MD.index.get_level_values('dt') <= current_date)]
            
            tickers_on_date = df_slice.loc[df_slice.index.get_level_values('dt') == current_date].index.get_level_values('Ticker')
                        
            df_current_history = df_slice[df_slice.index.get_level_values('Ticker').isin(tickers_on_date)]
            
            daily_factors = calculate_factors_for_day_optimized(current_date, df_current_history.copy(), factor_params)

            daily_factors.rename(columns={'Similar_Low_Volatility': self.factor_name }, inplace=True)
            database['pre_T_N'] = daily_factors[[self.factor_name]]
            return database

    def prepare_T_data(self, database):
        return database

    def calculate(self, database):
        if database.get("skip", False):
            return pd.Series({self.factor_name: np.nan})
        else:
            return database['pre_T_N']
