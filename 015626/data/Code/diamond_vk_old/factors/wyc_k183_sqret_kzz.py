from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k183_sqret_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','volume']
        super(wyc_k183_sqret_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        close = df['close'].between_time(data_morning_begin, trade_stop_time)
        close = close.groupby(close.index.date).last()
        close.index = pd.to_datetime(close.index)

        n = 6
        r = close / ts_max(close, 10) -1
        factor = np.sqrt(ts_mean(ts_sum(r ** 2, n), n))
        factor = factor.replace([np.inf, -np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor