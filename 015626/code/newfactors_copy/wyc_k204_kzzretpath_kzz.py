from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k204_kzzretpath_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close']
        super(wyc_k204_kzzretpath_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        ret_path = abs(df['close'].pct_change().between_time(data_morning_begin, trade_stop_time))
        ret_path = ret_path.groupby(ret_path.index.date).mean()
        ret_path.index = pd.to_datetime(ret_path.index)

        factor = ret_path
        factor.index = pd.to_datetime(factor.index.date)
        factor = factor.replace([np.inf,-np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor