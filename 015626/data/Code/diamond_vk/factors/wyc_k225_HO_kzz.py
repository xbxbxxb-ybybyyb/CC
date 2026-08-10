from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k225_HO_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['high_daily', 'open_daily']
        super(wyc_k225_HO_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = df['high_daily'] / df['open_daily']
        factor = factor.replace([np.inf,-np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor