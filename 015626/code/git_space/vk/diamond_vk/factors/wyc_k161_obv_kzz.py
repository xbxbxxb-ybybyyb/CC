from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k161_obv_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close_daily','volume_daily']
        super(wyc_k161_obv_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        close = df['close_daily']
        volume = df['volume_daily']

        con1 = close > ts_delay(close, 1)
        OBV = pd.DataFrame(columns=close.columns, index = close.index)
        OBV[con1] = volume
        con2 = close < ts_delay(close, 1)
        OBV[~con1 & con2] = -1 * volume
        OBV[~con1 & ~con2] = 0
        factor = ts_sum(OBV, 20)

        factor = factor.replace([np.inf, -np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor