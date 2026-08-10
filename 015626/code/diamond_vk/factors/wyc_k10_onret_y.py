from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k10_onret_y(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['kzz_onret', 'close']
        super(wyc_k10_onret_y, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        kzz_onret = df['kzz_onret'] 
        kzz_close = df['close']
        clist = list(set(kzz_close.columns) & set(kzz_onret.columns))
        clist.sort()

        factor = ts_sum(kzz_onret, 10)[clist]

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor