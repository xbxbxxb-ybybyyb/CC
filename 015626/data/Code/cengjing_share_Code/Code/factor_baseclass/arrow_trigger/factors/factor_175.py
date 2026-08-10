from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class factor_175(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't-1'
        required_columns = ['transaction', 'order', 'order_raw']
        super(factor_175, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            data = df['order'][stk]
            data_raw = df['order_raw'][stk]
            data_txn = df['transaction'][stk]
            data['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data.dt]
            data = data[data.MDTime >= 93000000000]
            data_raw['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data_raw.dt]
            data_raw = data_raw[data_raw.MDTime >= 93000000000]
            data_txn['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data_txn.dt]
            data_txn = data_txn[data_txn.MDTime >= 93000000000]

            data = data[data.OrderBSFlag == 1]
            if stk.endswith('SH'):
                data_raw = data_raw[(data_raw.OrderType == 10) & (data_raw.OrderBSFlag == 1)]
                factor[stk] = -1 * data_raw.OrderQty.sum() / data.OrderQty.sum()
            else:
                data_txn = data_txn[(data_txn.TradeType == 1) & (data_txn.TradeBSFlag == 1)]
                factor[stk] = -1 * data_txn.TradeQty.sum() / data.OrderQty.sum()
            
        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T
        factor = factor.replace([np.inf, -np.inf], np.nan)
        
        return factor