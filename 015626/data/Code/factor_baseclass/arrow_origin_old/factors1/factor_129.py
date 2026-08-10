from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd
from sklearn import linear_model
lr = linear_model.LinearRegression()

class factor_129(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't-1'
        required_columns = ['order']
        super(factor_129, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            data = df['order'][stk]
            data['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data.dt]
            data = data[data.MDTime >= 93000000000]
            data = data.set_index('MDTime')
            data1 = data.copy()
            data1.OrderQty = data1.OrderQty * data1.OrderPrice * (data1.OrderBSFlag == 1)
            data2 = data.copy()
            data2.OrderQty = data2.OrderQty * data2.OrderPrice * (data2.OrderBSFlag == 2)
            temp = (data1.OrderQty.cumsum() - data2.OrderQty.cumsum()).to_frame().reset_index()
            lr.fit(temp[['MDTime']], temp[['OrderQty']])       
            factor[stk] = (lr.predict(temp[['MDTime']]) - temp[['OrderQty']]).std().values[0] * -1
            
        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T
        factor = factor.replace([np.inf, -np.inf], np.nan)
        
        return factor