from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k214_updownstd_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close']
        super(wyc_k214_updownstd_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        chg_up = df['close'].pct_change().between_time(data_morning_begin, trade_stop_time)
        chg_down = chg_up.copy()
        chg_up[chg_up < 0] = 0
        chg_down[chg_down > 0] = 0
        std_up = chg_up.groupby(chg_up.index.date).std()
        std_down = chg_down.groupby(chg_down.index.date).std()

        factor = std_up - std_down
        factor.index = pd.to_datetime(factor.index)
        factor = factor.replace([np.inf,-np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor