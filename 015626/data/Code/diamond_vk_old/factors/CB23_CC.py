from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB23_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','open']
        super(CB23_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        close = df['close'].between_time(data_morning_begin, trade_stop_time)
        close = close.groupby(close.index.date).last()
        close.index = pd.to_datetime(close.index)
        opendf = df['open'].between_time(data_morning_begin, trade_stop_time)
        opendf = opendf.groupby(opendf.index.date).first()
        opendf.index = pd.to_datetime(opendf.index)

        factor = abs(ts_mean(close/opendf - 1, 8))

        factor.index = pd.to_datetime(factor.index)
        factor = factor.replace([-np.inf, np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor