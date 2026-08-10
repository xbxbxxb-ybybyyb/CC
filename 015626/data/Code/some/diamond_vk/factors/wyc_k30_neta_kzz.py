from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k30_neta_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','amount']
        super(wyc_k30_neta_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        # （成交价上涨部分对应的成交额-下跌部分对应的成交额）/总成交额
        c = np.sign(df['close'].pct_change().between_time(data_morning_begin, trade_stop_time))
        a = df['amount'].between_time(data_morning_begin, trade_stop_time)

        f = a * c
        factor = f.groupby(f.index.date).sum() / a.groupby(a.index.date).sum()
        factor = abs(factor) * -1
        factor.index = pd.to_datetime(factor.index)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor