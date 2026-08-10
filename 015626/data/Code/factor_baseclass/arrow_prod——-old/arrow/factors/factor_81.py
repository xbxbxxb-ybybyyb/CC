from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd


class factor_81(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't'
        required_columns = ['tick', 'transaction']
        super(factor_81, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        mean_list = []
        for stk in df['universe']:
            data = df['tick'][stk]
            data_t = df['transaction'][stk]
            data['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data.dt]
            data = data[(data.MDTime > 92400000000) & (data.MDTime < 92600000000)]
            data_t['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data_t.dt]
            data_t = data_t[data_t.MDTime < 92600000000]
            data_t = data_t[data_t.TradeType == 0]
            if (len(data_t) == 0) or (len(data) == 0):
                factor[stk] = np.nan
                continue
            
            px = data_t.TradePrice.values[-1]
            qty = data_t.TradeQty.sum()
            factor[stk] = -(px * 1e10  - data.Buy1Price.values[0] * 1e10)/data.PreClosePx.values[0]/(px * qty - data.Buy1Price.values[0] * data.Buy1OrderQty.values[0])
    
        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T
        factor = factor.replace([np.inf, -np.inf], np.nan)
        
        return factor