from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k230_CL_stk(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close_stk', 'low_stk_daily']
        super(wyc_k230_CL_stk, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        temp = df['close_stk'].between_time(data_morning_begin, trade_stop_time)
        temp = temp.groupby(temp.index.date).mean()
        temp.index = pd.to_datetime(temp.index)

        low = df['low_stk_daily']

        factor = (ts_mean(temp, 30) - ts_min(low,30)) / ts_min(low,30)
        factor = factor.replace([np.inf,-np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor