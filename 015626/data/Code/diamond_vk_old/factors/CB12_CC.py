from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB12_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close']
        super(CB12_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        ret = df['close'].pct_change()
        temp_rsi = (ret>=0)
        temp_rsi2 = (ret<=0)

        upvol = ts_std(temp_rsi*ret, 220)
        downvol = ts_std(temp_rsi2*ret, 220) * -1
        realvol = ts_std(ret, 220)
        vwtc_r = (upvol-downvol)/realvol

        factor = vwtc_r[-10:].mean().to_frame() * -1

        factor = factor.replace([-np.inf, np.inf], np.nan)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor