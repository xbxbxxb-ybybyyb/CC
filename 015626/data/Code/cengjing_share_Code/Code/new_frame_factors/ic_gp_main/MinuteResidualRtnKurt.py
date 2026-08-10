import numpy as np
from future_factor import FutureFactor
from scipy.stats import kurtosis

class MinuteResidualRtnKurt(FutureFactor):
    '''
    Description: kurt(residual_return, 60),
                residual_return = typical_price / predicted_price - 1,
                typical_price = (close_000905.SH + open_000905.SH + high_000905.SH + low_000905.SH) / 4,
                predicted_price = linear_regression(x=range(1, 61), y=typical_price[-60:], intercept=True).predict(x=range(1, 61))
    Class: Price_Stat
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'main'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close','open','high','low']}
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 60
        close = data['close_000905.SH'].values
        close[close == 0] = np.nan
        op = data['open_000905.SH'].values
        op[op == 0] = np.nan
        high = data['high_000905.SH'].values
        high[high == 0] = np.nan
        low = data['low_000905.SH'].values
        low[low == 0] = np.nan
        
        x = np.array((np.ones(lb), np.arange(1, lb + 1)))
        y = (close[-lb:] + op[-lb:] + high[-lb:] + low[-lb:]) / 4
        b = np.linalg.inv(x.dot(x.T)).dot(x.dot(y))
        y_hat = b.dot(x)
        f = -kurtosis(y - y_hat)
        
        if np.isnan(f) or np.isinf(f):
            return 0
        else:
            return f