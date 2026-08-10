from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd


class factor_85(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't'
        required_columns = ['tick', 'order']
        super(factor_85, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        mean_list = []
        for stk in df['universe']:
            data = df['tick'][stk]
            data['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data.dt]
            data = data[data.MDTime < 92600000000]
            data_order = df['order'][stk]
            data_order['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data_order.dt]
            data_order = data_order[data_order.MDTime < 92600000000]
            
            MaxPx = data['MaxPx'].values[0]
            data_order = data_order[(data_order.OrderType == 2) & (data_order.OrderBSFlag == 1)]
            MaxPxOrder = data_order[data_order.OrderPrice == MaxPx].OrderQty.sum()
            totalOrder = data_order.OrderQty.sum()
            factor[stk] = -MaxPxOrder/totalOrder
            
        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T
        factor = factor.replace([np.inf, -np.inf], np.nan)
        
        return factor