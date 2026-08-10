from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_mf20_positionskew(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['position_IC.CFE', 'recent_month_mask']
        super(wyc_mf20_positionskew, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=4, **kwargs)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        posi = df['position_IC.CFE'][df['recent_month_mask']].sum(axis = 1).to_frame()

        posi = posi.between_time(futures_data_morning_begin, trade_stop_time)

        factor = posi.groupby(posi.index.date).skew() 
        factor = ts_rank(factor, 2)

        factor.index.names = ['dt']
        factor.index = pd.to_datetime(factor.index)
        factor.columns = [columnname]

        return factor