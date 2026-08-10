from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k205_vwaptwap_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns= ['close', 'amount_daily', 'volume_daily']
        super(wyc_k205_vwaptwap_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        vwap = df['amount_daily'] / df['volume_daily']

        twap = df['close'].between_time(data_morning_begin, trade_stop_time)
        twap = twap.groupby(twap.index.date).mean()
        twap.index = pd.to_datetime(twap.index)

        factor = vwap / twap - 1
        factor.index = pd.to_datetime(factor.index.date)
        factor = factor.replace([np.inf,-np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor