from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class factor_251(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't'
        required_columns = ['order']
        super(factor_251, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            data = df['order'][stk]
            data['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data.dt]

            data['OrderMoney'] = data.OrderPrice * data.OrderQty
            data = data[(data.OrderMoney < 20000) & (data.MDTime < 92000000000)]
            data_buy = data[data.OrderBSFlag == 1]
            data_sell = data[data.OrderBSFlag == 2]

            factor[stk] = data_buy.OrderMoney.sum() / (data_buy.OrderMoney.sum() + data_sell.OrderMoney.sum())

        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T
        factor = factor.replace([np.inf, -np.inf], np.nan)
        return factor
