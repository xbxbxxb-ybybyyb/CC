from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k216_stddiff_kzzstk(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close_stk_daily', 'close_daily']
        super(wyc_k216_stddiff_kzzstk, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        chg_kzz = df['close_daily'].pct_change()
        chg_stk = df['close_stk_daily'].pct_change()
        N = 30
        factor = ts_std(chg_stk, N) - ts_std(chg_kzz, N)
        factor = factor * -1

        factor = factor.replace([np.inf,-np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor