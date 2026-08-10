from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB25_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','open','close_stk','open_stk']
        super(CB25_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):        
        f1 = ts_mean(df['close'][-90:],10)
        f1 = ts_reg_beta(f1, 60)[-20:]
        factor = abs(f1.mean()).to_frame()
        factor = factor.replace([-np.inf, np.inf], np.nan)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor