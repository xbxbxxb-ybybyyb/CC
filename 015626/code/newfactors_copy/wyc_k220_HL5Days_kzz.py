from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k220_HL5Days_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close_daily', 'open_daily', 'high_daily', 'low_daily']
        super(wyc_k220_HL5Days_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        _high = ts_max(df['high_daily'], 5)
        _low = ts_min(df['low_daily'], 5)
        factor = (_high - _low) / df['close_daily'] * (df['close_daily'] / df['open_daily'].shift(5) - 1)

        factor = factor.replace([np.inf,-np.inf], np.nan)
        factor = abs(factor.sub(factor.mean(axis = 1), axis = 0))

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor