import pandas as pd
import numpy as np
from numpy.lib.stride_tricks import as_strided
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_zxj_MD_Factor09_modified(BaseFactor):
    strategy_name = "neptune"
    factor_name = "zxj_MD_Factor09_modified"
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
            df_MD['adj_close'] = df_MD['close'] * df_MD['adjfactor']
            market_return_daily = df_MD.groupby('dt')['pct_chg'].mean()
            df_MD = df_MD.join(market_return_daily.rename('market_return'), on='dt')
            df_MD['excess_return'] = (df_MD['pct_chg'] - df_MD['market_return']) / 100
            
            factor_params = {
                'RW_r': 6, 'HW_r': 120, 'H_r': 6, 'Threshold_r': 0.40, 'Holding_Time_r': 5,
                'RW_v': 5, 'HW_v': 20, 'Threshold_v': 0.40, 'Holding_Time_v': 4,
            }

            def process_single_stock_vectorized(stock_data, params):
                
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
                dates = stock_data.index
                n_days = len(adj_close)

                # 初始化结果数组
                similar_reverse_factors = np.full(n_days, np.nan)
                similar_low_vol_factors = np.full(n_days, np.nan)
                counts_r = np.zeros(n_days, dtype=int)
                counts_v = np.zeros(n_days, dtype=int)

                
                def zscore(a, axis=-1):
                    mean = np.mean(a, axis=axis, keepdims=True)
                    std = np.std(a, axis=axis, keepdims=True)
                    std[std < 1e-9] = 1.0
                    return (a - mean) / std

                #计算相似反转因子  ---
                min_days_r = HW_r + RW_r
                if n_days >= min_days_r:
                    shape = (n_days - RW_r + 1, RW_r)
                    strides = (adj_close.strides[0], adj_close.strides[0])
                    all_current_sequences_r = as_strided(adj_close, shape=shape, strides=strides)

                    num_windows_r = HW_r - RW_r + 1
                    shape_3d = (n_days - min_days_r + 1, num_windows_r, RW_r)
                    s0, s1 = adj_close.strides[0], adj_close.strides[0]
                    strides_3d = (s0, s0, s1)
                    all_history_windows_r = as_strided(adj_close, shape=shape_3d, strides=strides_3d)

                    start_idx = min_days_r - 1
                    current_seqs_aligned = all_current_sequences_r[start_idx - RW_r + 1:, :]
                    
                    current_std = zscore(current_seqs_aligned, axis=1)
                    history_std = zscore(all_history_windows_r, axis=2)

                    correlations_r = np.einsum('ik,ijk->ij', current_std, history_std) / RW_r
                    
                    for i in range(correlations_r.shape[0]):
                        day_idx = start_idx + i
                        
                        valid_indices = np.where(np.abs(correlations_r[i]) >= Threshold_r)[0]
                        count_r = len(valid_indices)
                        counts_r[day_idx] = count_r
                        
                        if count_r < 2: continue

                        search_block_start_idx = day_idx - HW_r - RW_r + 1
                        return_start_indices = search_block_start_idx + valid_indices + RW_r
                        future_return_indices = return_start_indices[:, None] + np.arange(Holding_Time_r)

                        if future_return_indices.size > 0 and future_return_indices[-1, -1] < n_days:
                            future_returns_matrix = excess_returns[future_return_indices]
                            cumulative_returns = np.nanprod(1 + future_returns_matrix, axis=1) - 1
                            signed_returns = cumulative_returns * np.sign(correlations_r[i, valid_indices])
                            
                            n = count_r
                            decay_lambda = np.log(2) / H_r
                            k = np.arange(1, n + 1)
                            weights = np.exp(decay_lambda * k)
                            weights /= np.sum(weights)
                            weighted_avg_return = np.sum(signed_returns * weights)
                            similar_reverse_factors[day_idx] = -weighted_avg_return

                # ---计算相似低波因子 ---
                min_days_v = HW_v + RW_v
                if n_days >= min_days_v:
                    num_windows_v = HW_v - RW_v + 1
                    shape_current_v = (n_days - RW_v + 1, RW_v)
                    strides_current_v = (adj_close.strides[0], adj_close.strides[0])
                    all_current_sequences_v = as_strided(adj_close, shape=shape_current_v, strides=strides_current_v)

                    shape_3d_v = (n_days - min_days_v + 1, num_windows_v, RW_v)
                    s0, s1 = adj_close.strides[0], adj_close.strides[0]
                    strides_3d_v = (s0, s0, s1)
                    all_history_windows_v = as_strided(adj_close, shape=shape_3d_v, strides=strides_3d_v)
                    
                    start_idx_v = min_days_v - 1
                    current_seqs_aligned_v = all_current_sequences_v[start_idx_v - RW_v + 1:, :]
                    
                    current_std_v = zscore(current_seqs_aligned_v, axis=1)
                    history_std_v = zscore(all_history_windows_v, axis=2)

                    correlations_v = np.einsum('ik,ijk->ij', current_std_v, history_std_v) / RW_v

                    for i in range(correlations_v.shape[0]):
                        day_idx = start_idx_v + i
                        
                        valid_indices_v = np.where(np.abs(correlations_v[i]) >= Threshold_v)[0]
                        count_v = len(valid_indices_v)
                        counts_v[day_idx] = count_v

                        if count_v < 2: continue

                        search_block_start_idx_v = day_idx - HW_v - RW_v + 1
                        return_start_indices_v = search_block_start_idx_v + valid_indices_v + RW_v
                        future_return_indices_v = return_start_indices_v[:, None] + np.arange(Holding_Time_v)

                        if future_return_indices_v.size > 0 and future_return_indices_v[-1, -1] < n_days:
                            future_returns_matrix_v = excess_returns[future_return_indices_v]
                            cumulative_returns_v = np.nanprod(1 + future_returns_matrix_v, axis=1) - 1
                            std_dev = np.std(cumulative_returns_v, ddof=1)
                            if std_dev > 1e-9:
                                similar_low_vol_factors[day_idx] = 1 / std_dev

                
                result_df = pd.DataFrame({
                    'Similar_Reverse': similar_reverse_factors,
                    'Similar_Low_Volatility': similar_low_vol_factors,
                    'Count_Reverse': counts_r,
                    'Count_Low_Volatility': counts_v
                }, index=dates)

                return result_df.dropna(subset=['Similar_Reverse', 'Similar_Low_Volatility'], how='all')

            def calculate_all_factors_fully_vectorized(df_MD, params):
                
                print("Starting vectorized factor calculation for all stocks...")
                
                df_MD = df_MD.sort_index()

                all_results = df_MD.groupby('Ticker', group_keys=False).apply(
                    process_single_stock_vectorized, params=params
                )

                print("Factor calculation complete.")
                
                swapped_results = all_results.swaplevel('dt','Ticker')
                named_results = swapped_results.rename_axis(['Ticker', 'dt'])
                
                final_results = named_results.reorder_levels(['dt', 'Ticker']).sort_index()

                return final_results

            daily_factors = calculate_all_factors_fully_vectorized(df_MD, factor_params)
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
