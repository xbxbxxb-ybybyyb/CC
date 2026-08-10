from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k22_vs_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['volume']
        super(wyc_k22_vs_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        a = df['volume'].between_time(data_morning_begin, trade_stop_time)
        factor = a.groupby(a.index.date).sum()
        factor.index = pd.to_datetime(factor.index)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor