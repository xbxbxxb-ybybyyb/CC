from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB14_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','volume']
        super(CB14_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        tday = df['close'].index.date[-1]

        hc = df['close'][-400:].pct_change()
        hcv = df['volume'][-400:].pct_change()
        upclose = hc > 0
        upvolume = hcv > 0

        aa = upclose*upvolume
        vwtc_r = ts_sum(aa, 220)
        vwtc_r = vwtc_r.loc[tday:].between_time(datetime.time(14,0), trade_stop_time)
        factor = vwtc_r.mean().to_frame()
        factor = factor.replace([-np.inf, np.inf], np.nan)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor