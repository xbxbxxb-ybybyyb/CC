from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k192_stdv_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['volume']
        super(wyc_k192_stdv_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        # （成交价上涨部分对应的成交额-下跌部分对应的成交额）/总成交额
        volume = df['volume'].between_time(data_morning_begin, trade_stop_time)
        volume = volume.groupby(volume.index.date).sum()
        volume.index = pd.to_datetime(volume.index)

        factor = ts_std(volume, 10)
        factor = factor.replace([np.inf, -np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor