from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd


class factor_400(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 'all'
        required_columns = ['transaction_t', 'transaction_t_1']
        super(factor_400, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            data_t = df['transaction_t'][stk]
            data_t_1 = df['transaction_t_1'][stk].set_index('dt').between_time('915','926').reset_index()

            data_t = data_t[data_t.TradeType == 0]
            data_t_1 = data_t_1[data_t_1.TradeType == 0]

            if (len(data_t) == 0) or (len(data_t_1) == 0):
                factor[stk] = np.nan
                continue

            factor[stk] = data_t.groupby('TradeBuyNo').count().shape[0] / data_t_1.groupby('TradeBuyNo').count().shape[0]
            
            
        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T        
        return factor
