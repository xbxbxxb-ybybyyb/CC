from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k4_maxpct_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close']
        super(wyc_k4_maxpct_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        data = df['close'][-242:].between_time(data_morning_begin,trade_stop_time)
        p = data.groupby(data.index.date)
        factor = p.last() / p.min() - 1
        factor.index = pd.to_datetime(factor.index)

        factor = factor.replace([np.inf, -np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor