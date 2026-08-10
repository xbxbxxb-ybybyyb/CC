from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB31_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close']
        super(CB31_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        tday = df['close'].index.date[-1]

        close = df['close'][-200:]
        cm = ts_mean(close, 60)
        cs = ts_std(close, 60)

        bb = cm+2*cs

        f = (close/bb).loc[tday:].between_time(datetime.time(14,0), trade_stop_time)
        factor = f.mean().to_frame() * -1

        factor = factor.replace([-np.inf, np.inf], np.nan)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor