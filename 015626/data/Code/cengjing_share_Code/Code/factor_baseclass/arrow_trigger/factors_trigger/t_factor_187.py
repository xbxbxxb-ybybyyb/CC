from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class t_factor_187(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't'
        required_columns = ['tick']
        super(t_factor_187, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            data = df['tick'][stk]
            data['MDTime'] = [pd.Timestamp(x) for x in data.dt]
            i = data.MDTime.to_list()[0].strftime('%Y%m%d')
            data = data[data.MDTime >= pd.Timestamp(int(i[:4]),int(i[4:6]),int(i[-2:]),9,29,59)]

            MaxTime = data[data.LastPx == data.LastPx.max()].MDTime.values[0]
            MaxTime = (pd.Timestamp(MaxTime) - pd.Timestamp(int(i[:4]),int(i[4:6]),int(i[-2:]),9,29,59)).seconds
            if MaxTime > 12600:
                MaxTime = MaxTime - 5400
            MaxTime = np.max([0, MaxTime])
            factor[stk] = -1*  MaxTime
            
        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T
        factor = factor.replace([np.inf, -np.inf], np.nan)
        
        return factor