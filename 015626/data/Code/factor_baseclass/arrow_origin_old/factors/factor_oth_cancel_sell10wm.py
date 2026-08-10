from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd


class factor_oth_cancel_sell10wm(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't-1'
        required_columns = ['transaction', 'order', 'order_raw']
        super(factor_oth_cancel_sell10wm, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            data_t_1 = df['transaction'][stk]
            order = df['order'][stk]
            order['OrderMoney'] = order.OrderPrice * order.OrderQty 
            order_raw = df['order_raw'][stk]
            order_raw['OrderMoney'] = order_raw.OrderPrice * order_raw.OrderQty 

            if len(data_t_1) == 0:
                factor[stk] = np.nan
                continue

            max_end_time = data_t_1[data_t_1.TradePrice == data_t_1.TradePrice.max()].iloc[0]['dt']
            
            if stk.endswith('SH'):
                order_raw = order_raw[order_raw['dt'] < max_end_time]
                order_raw = order_raw[order_raw.OrderMoney > 100000]
                factor[stk] = order_raw[(order_raw.OrderType == 10) & (order_raw.OrderBSFlag == 2)].OrderMoney.sum()
            else:
                data_t_1['indexJoin'] = data_t_1.TradeBuyNo + data_t_1.TradeSellNo
                data_t_1 = data_t_1.set_index('indexJoin').join(order.rename(columns = {'OrderIndex':'indexJoin'}).set_index('indexJoin')[['OrderPrice']])
                data_t_1 = data_t_1[(data_t_1['dt'] < max_end_time) & (data_t_1.TradeType == 1)]
                data_t_1['Money'] = data_t_1.TradeQty * data_t_1.OrderPrice
                data_t_1 = data_t_1[data_t_1['Money'] > 100000]
                factor[stk] = data_t_1[data_t_1.TradeBSFlag == 2].Money.sum()
            
        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T        
        return factor
