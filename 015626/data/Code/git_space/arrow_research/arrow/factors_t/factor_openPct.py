from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd


class factor_openPct(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't'
        required_columns = ['tick', 'transaction']
        super(factor_openPct, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            data = df['tick'][stk]
            data['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data.dt]
            data = data[data.MDTime < 92600000000].iloc[-1]
            tran = df['transaction'][stk]
            tran['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in tran.dt]
            tran = tran[tran.MDTime < 92600000000].iloc[-1]

            if len(data) > 0:
                factor[stk] = tran.TradePrice / data.PreClosePx - 1
            else:
                factor[stk] = np.nan
            
        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T
        factor = factor.replace([np.inf, -np.inf], np.nan)
        
        return factor
