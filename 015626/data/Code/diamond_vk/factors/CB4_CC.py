from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB4_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','volume']
        super(CB4_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        f1 = df['close'][-190:]
        f2 = df['volume'][-190:]

        f = f1.rolling(180, min_periods = 30).corr(f2)
        f = f[-10:]
        factor = f.mean().to_frame()

        factor = factor.replace([-np.inf, np.inf], np.nan)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor