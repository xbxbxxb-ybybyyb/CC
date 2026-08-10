from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd


class factor_72(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't'
        required_columns = ['transaction', 'order', 'order_raw']
        super(factor_72, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        mean_list = []
        for stk in df['universe']:
            data_t = df['transaction'][stk]
            data_o = df['order'][stk]
            data_o_r = df['order_raw'][stk]
            if stk[0] == '6':
                data_o_r['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data_o_r.dt]
                data_o_r = data_o_r[data_o_r.MDTime < 92600000000]
                factor[stk] = -(data_o_r.OrderQty * data_o_r.OrderPrice)[data_o_r.OrderType == 10].sum() / (data_o.OrderQty * data_o.OrderPrice).sum()
            else:
                data_t['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data_t.dt]
                data_t = data_t[data_t.MDTime < 92600000000]
                data_t['indexJoin'] = data_t.TradeBuyNo + data_t.TradeSellNo
                data_t = data_t.set_index('indexJoin').join(data_o.rename(columns = {'OrderIndex':'indexJoin'}).set_index('indexJoin')[['OrderPrice']])
                factor[stk] = -(data_t.TradeQty * data_t.OrderPrice)[data_t.TradeType == 1].sum() / (data_o.OrderQty * data_o.OrderPrice).sum()
            
        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T
        factor = factor.replace([np.inf, -np.inf], np.nan)
        
        return factor