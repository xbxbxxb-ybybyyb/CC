from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k2_retdiffstd_ks(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','close_stk','CB_ANAL_CONVPRICE']
        super(wyc_k2_retdiffstd_ks, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        ret_diff = df['close_stk'].pct_change() - df['close'].pct_change()
        factor = ts_std(ret_diff, 230)
      
        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor