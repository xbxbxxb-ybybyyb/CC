from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k154_TYP_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close_daily','high_daily','low_daily','volume_daily']
        super(wyc_k154_TYP_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):

        close = df['close_daily']
        high = df['high_daily']
        low = df['low_daily']
        volume = df['volume_daily']

        N = 20
        TYP = (high + low + close) / 3
        a = pd.DataFrame(columns = close.columns, index = close.index)
        a[TYP > ts_delay(TYP, 1)] = TYP * volume
        a[TYP <= ts_delay(TYP, 1)] = 0
        b = pd.DataFrame(columns = close.columns, index = close.index)
        b[TYP < ts_delay(TYP, 1)] = TYP * volume
        b[TYP >= ts_delay(TYP, 1)] = 0
        V1 = ts_sum(a, N) / ts_sum(b, N)
        factor = 100 - (100 / (1 + V1))
        factor = factor.replace([np.inf, -np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor