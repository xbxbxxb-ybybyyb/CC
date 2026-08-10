from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class t_factor_180(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't'
        required_columns = ['order','tick']
        super(t_factor_180, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            data_order = df['order'][stk]
            data_tick = df['tick'][stk]
            data_order['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data_order.dt]
            data_order = data_order[data_order.MDTime >= 93000000000]
            data_tick['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data_tick.dt]
            data_tick = data_tick[data_tick.MDTime >= 93000000000]

            data_order = data_order.set_index('MDTime')
            data_tick = data_tick.set_index('MDTime')
            data_tick = data_tick.loc[~data_tick.index.duplicated()][['Buy1Price', 'Sell1Price']]
            
            data = data_order.join(data_tick)
            data[['Buy1Price', 'Sell1Price']] = data[['Buy1Price', 'Sell1Price']].fillna(method = 'ffill')
            data[['Buy1Price', 'Sell1Price']] = data[['Buy1Price', 'Sell1Price']].replace(0, np.nan)
    
            b = data[(data.OrderPrice>data.Buy1Price) & (data.OrderBSFlag == 1)].OrderQty.sum()
            s = data[(data.OrderPrice<data.Sell1Price) & (data.OrderBSFlag == 2)].OrderQty.sum()

            if b + s > 0:
                factor[stk] = b/(b+s)
            else:
                factor[stk] = np.nan
                
        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T
        factor = factor.replace([np.inf, -np.inf], np.nan)
        
        return factor