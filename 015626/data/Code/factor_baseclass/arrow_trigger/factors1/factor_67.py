from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd


class factor_67(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't'
        required_columns = ['tick']
        super(factor_67, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        mean_list = []
        for stk in df['universe']:
            data = df['tick'][stk]
            data['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data.dt]
            data = data[(data.MDTime > 91500000000) & (data.MDTime < 92500000000)]
            temp = data[(data.MDTime>92000000000) & (data.Buy1Price>0)]
            if len(temp) == 0:
                factor[stk] = np.nan
                continue
            factor[stk] = data[(data.MDTime<92000000000) & (data.Buy1Price>0)].Buy1Price.min() / temp.Buy1Price.values[0]
            
        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T
        factor = factor.replace([np.inf, -np.inf], np.nan)
        
        return factor