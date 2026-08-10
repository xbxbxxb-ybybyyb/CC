from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k231_CM_stk(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close_stk']
        super(wyc_k231_CM_stk, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        temp = df['close_stk'].between_time(data_morning_begin, trade_stop_time)
        temp = temp.groupby(temp.index.date).last()
        temp.index = pd.to_datetime(temp.index)

        factor = temp / ts_mean(temp,30) - 1
        factor = factor.replace([np.inf,-np.inf], np.nan)
        factor = abs(factor.sub(factor.mean(axis = 1), axis = 0))

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor