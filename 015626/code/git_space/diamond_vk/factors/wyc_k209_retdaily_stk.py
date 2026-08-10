from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k209_retdaily_stk(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close_stk_daily']
        super(wyc_k209_retdaily_stk, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = df['close_stk_daily'].pct_change()

        factor.index = pd.to_datetime(factor.index.date)
        factor = factor.replace([np.inf,-np.inf], np.nan)
        factor = abs(factor.sub(factor.mean(axis = 1), axis = 0))

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor