from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k211_ocpxpath_stk(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close_stk', 'close_daily', 'open_daily']
        super(wyc_k211_ocpxpath_stk, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        px_path = abs(df['close_stk'].diff().between_time(data_morning_begin, trade_stop_time))
        px_path = px_path.groupby(px_path.index.date).sum()
        px_path.index = pd.to_datetime(px_path.index)

        oc_path = abs(df['close_daily'] - df['open_daily'])
        factor = oc_path / px_path

        factor = factor.replace([np.inf,-np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor