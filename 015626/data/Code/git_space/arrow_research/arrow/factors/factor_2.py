from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd


class factor_2(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't'
        required_columns = ['tick']
        super(factor_2, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        mean_list = []
        for stk in df['universe']:
            data = df['tick'][stk]
            data['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data.dt]
            data = data[(data.MDTime < 92600000000) & (data.LastPx > 0)]
            if len(data) == 0:
                factor[stk] = np.nan
                continue
            data = data.iloc[-1]
            temp_factor = (data.LastPx / data.PreClosePx - 1)
            factor[stk] = temp_factor
            mean_list.append(temp_factor)
        mean_value = np.nanmean(mean_list)
        for stk in df['universe']:
            factor[stk] = -abs(factor[stk] - mean_value)
            
        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T
        factor = factor.replace([np.inf, -np.inf], np.nan)
        
        return factor
