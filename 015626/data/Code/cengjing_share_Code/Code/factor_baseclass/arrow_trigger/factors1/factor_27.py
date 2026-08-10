from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd
from sklearn import linear_model
lr = linear_model.LinearRegression()

 
class factor_27(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't'
        required_columns = ['order']
        super(factor_27, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        mean_list = []
        for stk in df['universe']:
            data = df['order'][stk]
            data['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data.dt]
            data = data[data.MDTime < 92600000000]
            data = data[(data.OrderType == 2) & (data.OrderBSFlag == 1)]
            if len(data) == 0:
                factor[stk] = np.nan
                continue
            lr.fit(data[['MDTime']], data[['OrderPrice']])
            factor[stk] = (lr.predict(data[['MDTime']]) - data[['OrderPrice']]).std().values[0]
            
        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T
        factor = factor.replace([np.inf, -np.inf], np.nan)
        
        return factor