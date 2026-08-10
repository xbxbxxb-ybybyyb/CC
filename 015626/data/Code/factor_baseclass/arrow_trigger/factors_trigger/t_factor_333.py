from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class t_factor_333(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't'
        required_columns = ['transaction']
        super(t_factor_333, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            data = df['transaction'][stk]
            data['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data.dt]
            data = data[data.MDTime >= 93000000000]

            data = data[data.TradeType == 0]
            data_big_buy = data.groupby('TradeBuyNo').TradeMoney.sum()
            data_big_buy = data_big_buy[data_big_buy < 40000]

            data_big_sell = data.groupby('TradeSellNo').TradeMoney.sum()
            data_big_sell = data_big_sell[data_big_sell < 40000]

            factor[stk] = data_big_buy.sum() / (data_big_buy.sum() + data_big_sell.sum())

        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T
        factor = factor.replace([np.inf, -np.inf], np.nan)
        return factor
