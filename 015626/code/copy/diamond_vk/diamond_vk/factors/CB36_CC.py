from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB36_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['high','low']
        super(CB36_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        high = df['high'].between_time(data_morning_begin, trade_stop_time)
        low = df['low'].between_time(data_morning_begin, trade_stop_time)

        diff = high.groupby(high.index.date).max()- low.groupby(low.index.date).min()

        factor = abs(ts_reg_beta(diff, 20))

        factor.index = pd.to_datetime(factor.index)
        factor = factor.replace([-np.inf, np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor