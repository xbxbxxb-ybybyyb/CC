from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd


class factor_order_bo_buyc(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 'all'
        required_columns = ['transaction_t', 'transaction_t_1', 'tick_t', 'order_t_1']
        super(factor_order_bo_buyc, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            data_t = df['transaction_t'][stk]
            data_t_1 = df['transaction_t_1'][stk]
            tick_t = df['tick_t'][stk]
            order_t_1 = df['order_t_1'][stk]

            data_t = data_t[data_t.TradeType == 0]
            data_t_1 = data_t_1[(data_t_1.TradeType == 0) & (data_t_1.TradePrice > 0)]
            tick_t = tick_t[tick_t.PreClosePx > 0]

            if (len(data_t) == 0) or (len(data_t_1) == 0) or (len(tick_t) == 0):
                factor[stk] = np.nan
                continue

            open_px = data_t.iloc[-1]['TradePrice']
            pre_close = tick_t['PreClosePx'].iloc[-1]
            close = data_t_1.iloc[-1]['TradePrice']
            open_px = open_px / (pre_close / close)

            buy = order_t_1[order_t_1.OrderBSFlag == 1]

            factor[stk] = len(buy[buy.OrderPrice >= open_px])
            
        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T        
        return factor
