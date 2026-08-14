import pandas as pd
import numpy as np
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_zxj_Min_Factor05(BaseFactor):
    strategy_name = "neptunelong"
    factor_name = "zxj_Min_Factor05"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "zxj"
    factor_explain = "成交量博弈因子"
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

        

        def get_game_factor_vectorized(df: pd.DataFrame, value_col: str, sort_key_col: str) -> pd.Series:
            """
            计算核心“博弈”因子的向量化版本。
            对整个 DataFrame 进行操作，一次性计算所有 Ticker 的因子值。
            """
            # 过滤掉包含 NaN 的行，因为它们无法排序
            data_filtered = df[['Ticker', value_col, sort_key_col]].dropna()
            if data_filtered.empty:
                return pd.Series(index=df['Ticker'].unique(), dtype=np.float64)

            # 关键步骤：按 Ticker 和排序键对整个 DF 排序
            data_sorted = data_filtered.sort_values(['Ticker', sort_key_col], kind='mergesort')
            
            # 使用 groupby 来确保 cumsum 在每个 Ticker 内部进行
            grouped = data_sorted.groupby('Ticker')[value_col]
            
            # 计算前向累加和
            cumsum_f = grouped.cumsum()
            
            # 高效计算后向累加和
            total_sum = grouped.transform('sum')
            cumsum_b = total_sum - cumsum_f + data_sorted[value_col]
            
            # 计算差值，并在每个组内求和
            diff = cumsum_f - cumsum_b
            factor_series = diff.groupby(data_sorted['Ticker']).sum()
            
            return factor_series

        def calculate_all_factors_vectorized(df_day: pd.DataFrame):
            """
            为单日所有股票批量计算所有博弈因子。
            这是一个完全向量化的函数，取代了原来的循环。
            """
            # 0. 预处理和排序
            df_day = df_day.sort_values(['Ticker', 'MDTime']).reset_index(drop=True)

            # 1. 时间过滤
            morning_session_filter = (df_day['MDTime'] >= 93500000) & (df_day['MDTime'] <= 113000000)
            afternoon_session_filter = (df_day['MDTime'] >= 130000000) & (df_day['MDTime'] < 145700000)
            df_filtered = df_day[morning_session_filter | afternoon_session_filter].copy()

            # 移除数据量过少的股票
            ticker_counts = df_filtered['Ticker'].value_counts()
            valid_tickers = ticker_counts[ticker_counts >= 10].index
            df_filtered = df_filtered[df_filtered['Ticker'].isin(valid_tickers)]

            if df_filtered.empty:
                return None

            # 2. 批量计算中间指标 (使用 groupby 确保在股票内计算)
            grouped_by_ticker = df_filtered.groupby('Ticker')
            df_filtered['return_5m'] = grouped_by_ticker['LastPx'].pct_change(5)
            
            df_filtered['amplitude'] = (df_filtered['HighPx'] - df_filtered['LowPx']) / df_filtered['LastPx']
            df_filtered['amplitude'] = df_filtered['amplitude'].replace([np.inf, -np.inf], np.nan)

            cum_max_px = grouped_by_ticker['HighPx'].cummax()
            cum_min_px = grouped_by_ticker['LowPx'].cummin()
            
            # ▼▼▼ 修改点1：修改“日内相对位置”的定义以匹配研报 ▼▼▼
            # 研报定义为“相对此前最低位的涨幅”和“相对此前最高位的跌幅”的平均值 
            # (LastPx - cum_min_px + cum_max_px - LastPx) / 2 = (cum_max_px - cum_min_px) / 2
            df_filtered['intraday_pos'] = (cum_max_px - cum_min_px) / 2
            # ▲▲▲ 修改结束 ▲▲▲

            # 3. 批量调用向量化因子计算函数
            factor_vol_return = get_game_factor_vectorized(df_filtered, 'VolumeTrade', 'return_5m')
            factor_vol_pos = get_game_factor_vectorized(df_filtered, 'VolumeTrade', 'intraday_pos')
            factor_amplitude_game = get_game_factor_vectorized(df_filtered, 'amplitude', 'return_5m')

            # 4. 组合成 DataFrame
            df_today_factors = pd.DataFrame({
                '成交量博弈_raw': 0.5 * factor_vol_return.add(0.5 * factor_vol_pos, fill_value=0),
                '振幅博弈_raw': factor_amplitude_game
            })
            df_today_factors.index.name = 'Ticker'
            return df_today_factors


        daily_data = database['xdb_tick1m_cs']
        daily_data = daily_data.reset_index()
         # 使用向量化函数计算当日所有股票的因子
        df_today_factors = calculate_all_factors_vectorized(daily_data)

        for factor_col_raw in ['成交量博弈_raw', '振幅博弈_raw']:
            final_col_name = factor_col_raw.replace('_raw', '')
            mean = df_today_factors[factor_col_raw].mean()
            std = df_today_factors[factor_col_raw].std()
            if std > 1e-8:
                # 计算Z-Score后取绝对值
                df_today_factors[final_col_name] = ((df_today_factors[factor_col_raw] - mean) / std).abs()
            else:
                df_today_factors[final_col_name] = 0.0

        df_today_factors['多空博弈'] = 0.5 * df_today_factors['成交量博弈'] + 0.5 * df_today_factors['振幅博弈']
        
        current_date = pd.to_datetime(daily_data['dt'].iloc[0])
        df_to_store = df_today_factors[['成交量博弈']].copy()
        df_to_store.rename(columns={'成交量博弈': self.factor_name }, inplace=True) 
        df_to_store['dt'] = current_date #.strftime('%Y-%m-%d')
        df_to_store = df_to_store.reset_index()
        df_to_store.set_index(['dt', 'Ticker'], inplace=True)
        database['pre_T_N'] = df_to_store[[self.factor_name]]
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