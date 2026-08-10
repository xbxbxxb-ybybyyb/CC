from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k229_CL_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close', 'low_daily']
        super(wyc_k229_CL_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        temp = df['close'].between_time(data_morning_begin, trade_stop_time)
        temp = temp.groupby(temp.index.date).mean()
        temp.index = pd.to_datetime(temp.index)

        low = df['low_daily']

        factor = ts_mean(temp, 15) - ts_min(low,30)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor