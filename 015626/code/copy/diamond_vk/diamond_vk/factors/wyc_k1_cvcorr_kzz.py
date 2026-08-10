from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k1_cvcorr_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','volume']
        super(wyc_k1_cvcorr_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        tday = df['close'].index.date[-1]
        close = df['close'].loc[tday:]
        volume = df['volume'].loc[tday:]

        factor = close.corrwith(volume).to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor