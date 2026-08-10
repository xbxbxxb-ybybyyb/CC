from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k110_BR_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','high','low']
        super(wyc_k110_BR_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

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

        M=20
        factor = ts_sum(MAX(0,high-ts_delay(close,1)),M)/ts_sum(MAX(0,ts_delay(close,1)-low),M)
        factor = factor.replace([np.inf, -np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor