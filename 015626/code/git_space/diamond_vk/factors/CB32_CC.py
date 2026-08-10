from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB32_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close']
        super(CB32_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):

        hclose1 = df['close'].between_time(data_morning_begin, data_afternoon_end)
        hclose2 = df['close'].between_time(data_morning_begin, trade_stop_time)

        f1 = (hclose1.groupby(hclose1.index.date).last()/hclose1.groupby(hclose1.index.date).first()-1).shift(1)
        f1 = ts_sum(f1, 10)

        f2 = (hclose2.groupby(hclose2.index.date).last()/hclose2.groupby(hclose2.index.date).first()-1)
        factor = abs(f1+f2)

        factor.index = pd.to_datetime(factor.index)
        factor = factor.replace([-np.inf, np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor