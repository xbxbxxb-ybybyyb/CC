import numpy as np
from future_factor import FutureFactor
from scipy.stats import skew

class MinuteResidualRtnSkew(FutureFactor):
    '''
    Description:skew(residual_return, 60),
                residual_return = close_000905.SH / predicted_price - 1,
                predicted_price = linear_regression(x=range(1, 61), y=close_000905.SH[-60:], intercept=True).predict(x=range(1, 61))
    Class: Price_Stat
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 60
        close = data['close_000905.SH'].values
        close[close == 0] = np.nan
        
        x = np.array((np.ones(lb), np.arange(1, lb + 1)))
        y = close[-lb:]
        b = np.linalg.inv(x.dot(x.T)).dot(x.dot(y))
        y_hat = b.dot(x)
        f = -skew(y / y_hat - 1)
        
        if np.isnan(f) or np.isinf(f):
            return 0
        else:
            return f