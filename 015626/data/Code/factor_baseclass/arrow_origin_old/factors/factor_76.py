from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd


class factor_76(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't'
        required_columns = ['order', 'transaction']
        super(factor_76, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        mean_list = []
        for stk in df['universe']:
            data_t = df['transaction'][stk]
            data_o = df['order'][stk]
            data_t['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data_t.dt]
            data_o['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data_o.dt]
            data_t = data_t[data_t.MDTime < 92600000000]
            data_o = data_o[data_o.MDTime < 92600000000]
            
            px = data_t.TradePrice.values[-1]
            b = data_o[(data_o.OrderBSFlag == 1) & (data_o.OrderPrice >= px)]
            factor[stk] = -((b.OrderPrice - px)*b.OrderQty).sum()
            
        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T
        factor = factor.replace([np.inf, -np.inf], np.nan)
        
        return factor