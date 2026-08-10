from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class factor_185(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't-1'
        required_columns = ['tick', 'order']
        super(factor_185, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            data = df['tick'][stk]
            data_order = df['order'][stk]
            data['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data.dt]
            data = data[data.MDTime >= 93000000000]
            data_order['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data_order.dt]
            data_order = data_order[data_order.MDTime >= 93000000000]
            
            MinPx = data['MinPx'].values[0]
            data_order = data_order[data_order.OrderBSFlag == 1]
            MinPxOrder = data_order[data_order.OrderPrice == MinPx].OrderQty.sum()
            totalOrder = data_order.OrderQty.sum()
            factor[stk] = -1 * MinPxOrder/totalOrder

            
        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T
        factor = factor.replace([np.inf, -np.inf], np.nan)
        
        return factor