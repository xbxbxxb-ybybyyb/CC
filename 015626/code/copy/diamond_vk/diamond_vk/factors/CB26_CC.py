from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB26_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['open','low']
        super(CB26_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        low = df['low'][-240:].between_time(data_afternoon_begin, trade_stop_time)
        low = low.groupby(low.index.date).min()
        low.index = pd.to_datetime(low.index)
        opendf = df['open'][-240:].between_time(data_afternoon_begin, trade_stop_time)
        opendf = opendf.groupby(opendf.index.date).first()
        opendf.index = pd.to_datetime(opendf.index)

        factor = (low / opendf) * -1

        factor.index = pd.to_datetime(factor.index)
        factor = factor.replace([-np.inf, np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor