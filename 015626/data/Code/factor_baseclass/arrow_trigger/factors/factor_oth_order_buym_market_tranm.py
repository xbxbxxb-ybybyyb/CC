from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd


class factor_oth_order_buym_market_tranm(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't-1'
        required_columns = ['transaction', 'order']
        super(factor_oth_order_buym_market_tranm, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            data_t_1 = df['transaction'][stk]
            data_t_1 = data_t_1[(data_t_1.TradeType == 0) & (data_t_1.TradePrice > 0)]
            order = df['order'][stk]
            order['OrderMoney'] = order.OrderPrice * order.OrderQty 

            if len(data_t_1) == 0:
                factor[stk] = np.nan
                continue

            max_end_time = data_t_1[data_t_1.TradePrice == data_t_1.TradePrice.max()].iloc[0]['dt']
            temp = order[order['dt'] < max_end_time]

            temp = temp[temp.OrderBSFlag == 1]

            if stk.endswith('SH'):
                order_index_list = temp.OrderNO.tolist()
            else:
                order_index_list = temp.OrderIndex.tolist()

            factor[stk] = data_t_1[data_t_1['TradeBuyNo'].isin(order_index_list) & (data_t_1.TradeBSFlag == 1)].TradeMoney.sum()
            
        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T        
        return factor
