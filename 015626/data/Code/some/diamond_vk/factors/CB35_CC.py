from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB35_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','open','close_stk','open_stk']
        super(CB35_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):        
        hclose = df['close'].between_time(data_morning_begin, trade_stop_time)
        hopen = df['open'].between_time(data_morning_begin, trade_stop_time)

        diff = hclose.groupby(hclose.index.date).last()- hopen.groupby(hopen.index.date).first()

        factor = abs(ts_reg_beta(diff, 15))

        factor.index = pd.to_datetime(factor.index)
        factor = factor.replace([-np.inf, np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor