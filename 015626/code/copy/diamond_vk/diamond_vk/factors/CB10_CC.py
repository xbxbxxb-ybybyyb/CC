from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB10_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['volume', 'close']
        super(CB10_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        temp1 = df['close'][-50:].pct_change()
        temp2 = np.abs(df['volume'][-50:] * temp1)
        hdl_ind_r = ts_mean(temp2, 30)
        factor = hdl_ind_r[-10:].mean().to_frame()

        factor = factor.replace([-np.inf, np.inf], np.nan)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor