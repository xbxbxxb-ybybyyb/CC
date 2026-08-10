from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd


class factor_oth_abspath_ratio(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't-1'
        required_columns = ['transaction']
        super(factor_oth_abspath_ratio, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            data_t_1 = df['transaction'][stk]
            data_t_1 = data_t_1[(data_t_1.TradeType == 0) & (data_t_1.TradePrice > 0)]

            if len(data_t_1) == 0:
                factor[stk] = np.nan
                continue

            data_t_1['abs_px_diff'] = data_t_1['TradePrice'].diff().abs()
            max_end_time = data_t_1[data_t_1.TradePrice == data_t_1.TradePrice.max()].iloc[0]['dt']
            temp = data_t_1[data_t_1['dt'] < max_end_time]

            factor[stk] = data_t_1['abs_px_diff'].sum() / (data_t_1.TradePrice.max() - data_t_1.iloc[0]['TradePrice'])
            
        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T        
        return factor
