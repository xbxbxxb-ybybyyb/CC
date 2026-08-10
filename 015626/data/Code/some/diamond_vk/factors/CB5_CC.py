from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB5_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','high']
        super(CB5_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        f1 = df['close'][-5:]
        f2 = df['high'][-5:]

        f = f1/f2
        factor = f.mean().to_frame() * -1
        factor = factor.replace([-np.inf, np.inf], np.nan)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor