import pandas as pd
import numpy as np
from datetime import time as datetime_time 
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_zxj_Min_Factor03_new(BaseFactor):
    strategy_name = "neptune"
    factor_name = "zxj_Min_Factor03_new"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "zxj"
    factor_explain = "方正研报“待著而救”因子"
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

        def calculate_dzej_for_stock(stock_day_df: pd.DataFrame) -> float:
            trading_data = stock_day_df[stock_day_df['datetime'].dt.time >= datetime_time(9, 46)].copy()
            if len(trading_data) < 10:
                return np.nan

            huge_volume_moments = trading_data.nlargest(10, 'VolumeTrade')
            if huge_volume_moments.empty:
                return np.nan
            huge_volume_moments = huge_volume_moments.sort_values(by='datetime')

            time_diffs = huge_volume_moments['datetime'].diff()
            mask = (time_diffs.isnull()) | (time_diffs > pd.Timedelta(minutes=5))
            advantageous_moments = huge_volume_moments[mask]
            
            if advantageous_moments.empty:
                return np.nan

            following_coefficients = []
            stock_day_df_indexed = stock_day_df.set_index('datetime')
            
            for _, adv_moment in advantageous_moments.iterrows():
                adv_time = adv_moment['datetime']
                adv_volume = adv_moment['VolumeTrade']

                if adv_volume == 0:
                    continue
                
                start_follow = adv_time + pd.Timedelta(minutes=1)
                end_follow = adv_time + pd.Timedelta(minutes=5)
                
                follow_trades = stock_day_df_indexed.loc[start_follow:end_follow]
                follow_volume = follow_trades['VolumeTrade'].sum()
                
                coeff = follow_volume / adv_volume if adv_volume else np.nan
                following_coefficients.append(coeff)

            if not following_coefficients:
                return np.nan
            
            daily_factor = np.nanmean(following_coefficients)
            return daily_factor

        daily_data = database['xdb_tick1m_cs'] # TODO xdb_tick1m_cs

        daily_data = daily_data.reset_index()
        base_date = pd.to_datetime(daily_data['dt'].astype(str))
        mdtime_int = daily_data['MDTime']
        hours = mdtime_int // 10000000
        minutes = (mdtime_int % 10000000) // 100000
        seconds = (mdtime_int % 100000) // 1000
        time_deltas = pd.to_timedelta(hours, unit='h') + \
                      pd.to_timedelta(minutes, unit='m') + \
                      pd.to_timedelta(seconds, unit='s')
        
        daily_data['datetime'] = base_date + time_deltas

        agg_dict = {'VolumeTrade': 'sum'}
        daily_data_agg = daily_data.groupby(['Ticker', 'datetime']).agg(agg_dict).reset_index()

        daily_factors = daily_data_agg.groupby('Ticker').apply(calculate_dzej_for_stock)

        res = daily_factors.to_frame(name=self.factor_name)
        
        current_date = pd.to_datetime(daily_data['dt'].iloc[0])
        res['dt'] = current_date
        res.reset_index(inplace=True)
        res.set_index(['dt', 'Ticker'], inplace=True)
        
        database['pre_T_N'] = res[[self.factor_name]]
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