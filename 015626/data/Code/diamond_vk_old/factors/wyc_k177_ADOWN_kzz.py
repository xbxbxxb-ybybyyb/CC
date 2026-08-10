from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k177_ADOWN_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close']
        super(wyc_k177_ADOWN_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        close = df['close'].between_time(data_morning_begin, trade_stop_time)
        close = close.groupby(close.index.date).last()
        close.index = pd.to_datetime(close.index)

        N = 20
        DOWN = pd.DataFrame(columns = close.columns, index = close.index, dtype = 'float')
        DOWN[close <= ts_delay(close, 1)] = ts_std(close, N)
        DOWN[close > ts_delay(close, 1)] = 0
        factor = ts_mean(DOWN, N)
        factor = factor.replace([np.inf, -np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor