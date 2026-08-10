from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k43_DC_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','high','low']
        super(wyc_k43_DC_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):

        h = df['high'][-200:].between_time(data_afternoon_begin, trade_stop_time)
        lo = df['low'][-200:].between_time(data_afternoon_begin, trade_stop_time)
        h = h.groupby(h.index.date).max()
        lo = lo.groupby(lo.index.date).min()
        h.index = pd.to_datetime(h.index)
        lo.index = pd.to_datetime(lo.index)

        close = df['close'][-200:].between_time(data_afternoon_begin, trade_stop_time)
        close = close.groupby(close.index.date).last()
        close.index = pd.to_datetime(close.index)

        UPPER = h
        LOWER = lo
        MIDDLE = (UPPER+LOWER)/2
        factor = (close - MIDDLE) / MIDDLE * -1

        factor = factor.replace([np.inf, -np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor