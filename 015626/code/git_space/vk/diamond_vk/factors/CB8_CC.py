from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB8_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['high', 'low']
        super(CB8_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        tday = df['high'].index.date[-1]

        temp_high = df['high'].loc[tday:].between_time(datetime.time(14,0), trade_stop_time).max()
        temp_low = df['low'].loc[tday:].between_time(datetime.time(14,0), trade_stop_time).min()

        factor = ((temp_high-temp_low)/temp_low).to_frame()

        factor = factor.replace([-np.inf, np.inf], np.nan)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor