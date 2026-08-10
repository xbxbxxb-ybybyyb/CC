from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB15_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['volume']
        super(CB15_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        tday = df['volume'].index.date[-1]
        f1 = df['volume'].loc[tday:].between_time(datetime.time(14,0), trade_stop_time)
        factor = f1.skew().to_frame() * -1

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor