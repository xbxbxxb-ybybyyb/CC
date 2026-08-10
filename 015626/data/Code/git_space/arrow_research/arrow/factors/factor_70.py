from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd


class factor_70(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't'
        required_columns = ['tick']
        super(factor_70, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        mean_list = []
        for stk in df['universe']:
            data = df['tick'][stk]
            data['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data.dt]
            data = data[data.MDTime < 92600000000]
            data1 = data[data.MDTime<92000000000]  
            data2 = data[data.MDTime>92000000000] 
            if len(data1) == 0 or len(data2) == 0:
                factor[stk] = np.nan
                continue
            factor[stk] = (0.5 * (data2.Buy1Price.values[-1] + data2.Sell1Price.values[-1]) - data1.Buy1Price.values[-1]) / data1.PreClosePx.values[-1]
            
        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T
        factor = factor.replace([np.inf, -np.inf], np.nan)
        
        return factor