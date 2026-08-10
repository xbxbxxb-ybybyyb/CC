from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB2_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['volume', 'volume_stk']
        super(CB2_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        f1 = df['volume_stk'].between_time(data_morning_begin, trade_stop_time)[-215:]
        f2 = df['volume'].between_time(data_morning_begin, trade_stop_time)[-215:]

        f = f1.rolling(210, min_periods = 30).corr(f2)
        factor = f[-5:].mean().to_frame()

        factor = factor.replace([-np.inf, np.inf], np.nan)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor