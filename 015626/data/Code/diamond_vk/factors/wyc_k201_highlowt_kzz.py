from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k201_highlowt_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['high', 'low']
        super(wyc_k201_highlowt_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        fu = abs(df['high'] / df['low'] - 1).between_time(data_morning_begin, trade_stop_time)
        fu = fu.replace([np.inf, -np.inf], np.nan)
        fu = fu > 0.005
        fu = fu.groupby(fu.index.date).sum()
        fu.index = pd.to_datetime(fu.index)

        factor = fu.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor