from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class kzz_assuper(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['amount']
        super(kzz_assuper, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = df['amount'][-250:].between_time(data_morning_begin,trade_stop_time)
        factor = factor.groupby(factor.index.date).sum()
        factor.index = pd.to_datetime(factor.index)
      
        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor