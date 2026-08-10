from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd


class t_factor_oth_sellc(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't'
        required_columns = ['transaction']
        super(t_factor_oth_sellc, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            data_t_1 = df['transaction'][stk]
            data_t_1 = data_t_1[(data_t_1.TradeType == 0) & (data_t_1.TradePrice > 0)]

            if len(data_t_1) == 0:
                factor[stk] = np.nan
                continue

            max_end_time = data_t_1[data_t_1.TradePrice == data_t_1.TradePrice.max()].iloc[0]['dt']
            temp = data_t_1[data_t_1['dt'] < max_end_time]

            temp = temp[temp.TradeBSFlag == 2]
            temp = temp.groupby('TradeSellNo').TradeMoney.sum()

            factor[stk] = len(temp)
            
        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T        
        return factor
