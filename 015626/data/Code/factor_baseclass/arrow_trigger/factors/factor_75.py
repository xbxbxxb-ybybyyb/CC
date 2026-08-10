from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd


class factor_75(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't'
        required_columns = ['order', 'tick']
        super(factor_75, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        mean_list = []
        for stk in df['universe']:
            data_tick = df['tick'][stk]
            data_order = df['order'][stk]
            data_tick['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data_tick.dt]
            data_order['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data_order.dt]
            data_tick = data_tick[data_tick.MDTime < 92600000000]
            data_order = data_order[data_order.MDTime < 92600000000]
            data = data_order.set_index('MDTime')\
            .join(pd.DataFrame({'MDTime':np.arange(91500000000, 92500000000, 10000)}).set_index('MDTime')\
            .join(data_order.set_index('MDTime'))\
            .join(data_tick[['MDTime', 'Buy1Price']].set_index('MDTime'))\
            .fillna(method = 'ffill').dropna(subset = ['Buy1Price'])[['Buy1Price']]).drop_duplicates()
            
            b = data[(data.OrderPrice>data.Buy1Price) & (data.OrderBSFlag == 1)].OrderQty.sum()
            s = data[(data.OrderPrice<data.Buy1Price) & (data.OrderBSFlag == 2)].OrderQty.sum()
            factor[stk] = -b / (b + s) if (b + s) > 0 else np.nan
            
        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T
        factor = factor.replace([np.inf, -np.inf], np.nan)
        
        return factor