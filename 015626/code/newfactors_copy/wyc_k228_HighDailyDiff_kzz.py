from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k228_HighDailyDiff_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close', 'amount']
        super(wyc_k228_HighDailyDiff_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        temp = df['high'].between_time(data_morning_begin, trade_stop_time)
        temp = temp.groupby(temp.index.date).max()
        temp.index = pd.to_datetime(temp.index)

        f1 = ts_max(temp, 10) - ts_max(temp, 20)

        factor = f1 
        factor = abs(factor.sub(factor.mean(axis = 1), axis = 0))

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor