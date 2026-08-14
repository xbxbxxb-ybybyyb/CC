import pandas as pd
import numpy as np
import warnings
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

warnings.simplefilter(action='ignore', category=FutureWarning)

class factor_zxj_Min_Factor12(BaseFactor):
    strategy_name = "neptune"
    factor_name = "zxj_Min_Factor12"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "zxj"
    factor_explain = "协同效应"
    zcz_adjusted = "否"
    logic_type = ""
    low_cost = ""
    t_day_data = []

    xdb_data = [
        {
        'name': 'xdb_tick1m_cs', 
        'lag': 3,
    }]

    def pre_calculate_T_N_data(self, database):
        if database.get("skip", False):
            return database

        def calculate_volume_synergy(daily_minute_data: pd.DataFrame) -> pd.Series:
            """
            计算 '成交量协同' 因子。
            """
            df = daily_minute_data.copy()
            
            # --- 1. 识别协同群体 ---
            price_cols = ['OpenPx_1m', 'HighPx_1m', 'LowPx_1m', 'LastPx']
            all_rolling_prices = []
            for p_col in price_cols:
                for i in range(5):
                    all_rolling_prices.append(df.groupby('Ticker')[p_col].shift(i))

            price_df = pd.concat(all_rolling_prices, axis=1)
            
            price_mean = price_df.mean(axis=1)
            price_std = price_df.std(axis=1)
            
            upper_rail = price_mean + price_std
            lower_rail = price_mean - price_std
            
            df['state'] = 0
            df.loc[df['LastPx'] > upper_rail, 'state'] = 1
            df.loc[df['LastPx'] < lower_rail, 'state'] = -1
            
            # --- 2. 计算协同成交量 ---
            total_market_vol = df.groupby('MDTime')['VolumeTrade'].transform('sum')
            total_market_vol[total_market_vol == 0] = np.nan
            df['VolPct'] = df['VolumeTrade'] / total_market_vol
            
            df['GroupVolPct'] = df.groupby(['MDTime', 'state'])['VolPct'].transform('sum')
            df['SynergyVol'] = df['GroupVolPct'] - df['VolPct']
            
            # --- 3. 计算日度相关性 ---
            df.dropna(subset=['VolPct', 'SynergyVol'], inplace=True)
            factor_series = df.groupby('Ticker').apply(lambda x: x['VolPct'].corr(x['SynergyVol']))
            
            return factor_series.rename('成交量协同')

        def calculate_price_spread_synergy(daily_minute_data: pd.DataFrame) -> pd.Series:
            """
            计算 '协同价差' 因子。
            """
            df = daily_minute_data.copy()
            
            # --- 1. 计算分钟协同信号 ---
            df['ret_1m'] = df.groupby('Ticker')['LastPx'].pct_change()
            past_ret_mean = df.groupby('Ticker')['ret_1m'].transform(lambda x: x.shift(1).rolling(5).mean())
            df['ret_chg'] = df['ret_1m'] - past_ret_mean
            past_vol_mean = df.groupby('Ticker')['VolumeTrade'].transform(lambda x: x.shift(1).rolling(5).mean())
            df['vol_chg'] = df['VolumeTrade'] - past_vol_mean

            df['sign1'] = np.sign(df['ret_1m'])
            df['sign2'] = np.sign(df['ret_chg'])
            df['sign3'] = np.sign(df['vol_chg'])
            
            # --- 2. 构建日度协同矩阵 ---
            all_tickers = np.sort(df['Ticker'].unique())
            n_stocks = len(all_tickers)
            if n_stocks == 0:
                return pd.Series(dtype=np.float64, name='协同价差')
                
            pivoted = df.pivot_table(index='MDTime', columns='Ticker', values=['sign1', 'sign2', 'sign3'])
            
            T = len(pivoted.index)
            all_signs_3d = np.full((T, n_stocks, 3), np.nan)

            for i, sign_type in enumerate(['sign1', 'sign2', 'sign3']):
                if sign_type in pivoted.columns.get_level_values(0):
                    sign_df_slice = pivoted[sign_type].reindex(columns=all_tickers)
                    all_signs_3d[:, :, i] = sign_df_slice.values

            daily_synergy_matrix = np.zeros((n_stocks, n_stocks), dtype=np.int32)
            for i in range(n_stocks):
                synergy_counts = np.nansum(all_signs_3d[:, i:i+1, :] == all_signs_3d, axis=(0, 2))
                daily_synergy_matrix[i, :] = synergy_counts
                
            # --- 3. 寻找核心协同群并计算价差 ---
            np.fill_diagonal(daily_synergy_matrix, -1)
            top_30_indices = np.argsort(daily_synergy_matrix, axis=1)[:, -30:]
            
            last_prices = df.groupby('Ticker')['LastPx'].last()
            pre_closes = df.groupby('Ticker')['pre_close'].first()
            daily_returns_s = (last_prices / pre_closes - 1)
            daily_returns = daily_returns_s.reindex(all_tickers).values
            
            peer_returns = daily_returns[top_30_indices]
            
            mean_peer_returns = np.nanmean(peer_returns, axis=1)
            
            factor_values = daily_returns - mean_peer_returns
            
            return pd.Series(factor_values, index=all_tickers, name='协同价差')

        def process_daily_data(df: pd.DataFrame, current_dt: pd.Timestamp) -> pd.DataFrame:
            """
            处理单日数据。
            循环处理文件内每个 MDDate, 计算因子后再对结果求平均。
            """
            # 1. 初始数据准备
            if not isinstance(df.index, pd.MultiIndex) or 'Ticker' not in df.index.names:
                return pd.DataFrame()

            if df.empty or df.index.get_level_values('Ticker').empty:
                return pd.DataFrame()
                
            df.reset_index(inplace=True)
            
            # 2. 按 MDDate 循环计算因子
            unique_mddates = df['MDDate'].unique()
            mddate_results = []
            
            for mddate in unique_mddates:
                df_slice = df[df['MDDate'] == mddate].copy()
                
                fill_cols = ['LastPx', 'OpenPx_1m', 'HighPx_1m', 'LowPx_1m', 'VolumeTrade']
                if not all(col in df_slice.columns for col in fill_cols):
                    continue
                
                df_slice.sort_values(['Ticker', 'MDTime'], inplace=True)
                df_slice[fill_cols] = df_slice.groupby('Ticker')[fill_cols].transform('ffill')

                if df_slice.empty:
                    continue

                factor_vol_syn = calculate_volume_synergy(df_slice)
                factor_price_spread = calculate_price_spread_synergy(df_slice)
                
                result_slice = pd.concat([factor_vol_syn, factor_price_spread], axis=1)
                mddate_results.append(result_slice)

            if not mddate_results:
                return pd.DataFrame()

            # 3. 对所有 MDDate 的因子结果求平均
            all_mddate_factors = pd.concat(mddate_results)
            averaged_factors = all_mddate_factors.groupby(all_mddate_factors.index).mean()

            # 4. 截面标准化并合成最终因子
            f1 = averaged_factors['成交量协同']
            f2 = averaged_factors['协同价差']

            standardized_f1 = (f1 - f1.mean()) / f1.std()
            standardized_f2 = (f2 - f2.mean()) / f2.std()
            
            averaged_factors['协同效应'] = standardized_f1.fillna(0) + standardized_f2.fillna(0)

            # 5. 格式化最终输出
            averaged_factors['dt'] = current_dt
            result_df = averaged_factors.reset_index().rename(columns={'index': 'Ticker'})
            result_df = result_df.set_index(['dt', 'Ticker'])
            
            return result_df

        
        daily_data = database['xdb_tick1m_cs']
        current_dt = daily_data.index[0][0]
        daily_factors = process_daily_data(daily_data,current_dt)
        daily_factors.rename(columns={'协同效应': self.factor_name }, inplace=True)
        database['pre_T_N'] = daily_factors[[self.factor_name]]
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