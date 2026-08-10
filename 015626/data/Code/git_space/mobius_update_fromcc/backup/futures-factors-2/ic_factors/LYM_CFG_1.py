
# coding: utf-8

# In[ ]:


import numpy as np
from future_factor import FutureFactor
import pandas as pd
import bottleneck as bk

def ts_rank(data, d):
    # moving time-series rank for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if d == 1:
        output = data
    else:
        if isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_rank(data, window=d, min_count=int(d / 2), axis=0),
                                  index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_rank(data, window=d, min_count=int(d / 2), axis=0),
                               index=data.index, name=data.name)
        elif isinstance(data, np.ndarray):
            output = bk.move_rank(data, window=d, min_count=int(d / 2), axis=0)
    return output

class LYM_CFG_1(FutureFactor):
    data_type = 'IndexStock'
    days_past = 6
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum','BuyTradeNum','SellTradeNum','SellUniqueOrderNum','close']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None 
    handle_preadj = None


    def calculate(self, df):
        
        a = df['BuyTradeNum'][-1200:]
        b = df['BuyUniqueOrderNum'][-1200:]
        c = df['SellTradeNum'][-1200:]
        d = df['SellUniqueOrderNum'][-1200:]
        close = df['close'][-1230:]
        
        factor1 = (a - b - c + d).sum(axis = 1)
        factor1 = ts_rank(factor1, 1200)

        factor2 = ts_rank((close / close.shift(30) - 1).mean(axis = 1), 1200)

        factor = (factor1 + factor2 ** 2)[-1]

        return factor

