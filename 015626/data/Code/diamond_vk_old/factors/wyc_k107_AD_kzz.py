from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k107_AD_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','high','low','volume']
        super(wyc_k107_AD_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        
        close = df['close'].between_time(data_morning_begin, trade_stop_time)
        close = close.groupby(close.index.date).last()
        close.index = pd.to_datetime(close.index)
        high = df['high'].between_time(data_morning_begin, trade_stop_time)
        high = high.groupby(high.index.date).max()
        high.index = pd.to_datetime(high.index)
        low = df['low'].between_time(data_morning_begin, trade_stop_time)
        low = low.groupby(low.index.date).min()
        low.index = pd.to_datetime(low.index)
        volume = df['volume'].between_time(data_morning_begin, trade_stop_time)
        volume = volume.groupby(volume.index.date).sum()
        volume.index = pd.to_datetime(volume.index)

        factor = -1 * ts_sum(((close-low)-(high-close))/(high-low)*volume,30)
        factor = factor.replace([np.inf, -np.inf], np.nan)
      
        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor