from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class factor_71(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't'
        required_columns = ['order', 'order_raw', 'transaction']
        super(factor_71, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            order = df['order'][stk]
            order_raw = df['order_raw'][stk]
            trans = df['transaction'][stk]
            order_qty = order.OrderQty.sum()
            
            if stk.endswith('SH'):
                factor[stk] = -order_raw[order_raw.OrderType == 10].OrderQty.sum() / order_qty
            else:
                factor[stk] = -trans[trans.TradeType == 1].TradeQty.sum() / order_qty
            
        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T
        factor = factor.replace([np.inf, -np.inf], np.nan)
        
        return factor