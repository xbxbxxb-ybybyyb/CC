import numpy as np
from future_factor import FutureFactor

class MinuteLatestResidualAbs(FutureFactor):
    '''
    Description: abs(mean(linear_regression_residual(x=range(1, 121), y=close_000905.SH[-120:], intercept=True), 5))
    Class: Convexity
    Author: hefj, modified by lixr
    '''
    
    data_type = 'Future'
    instrument_type = 'main'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 120
        close = data['close_000905.SH'].values
        close[close == 0] = np.nan
        
        x = np.concatenate((np.ones((lb, 1)), np.arange(1, lb + 1).reshape((lb, -1))), axis=1)
        close_temp = close[-lb:]
        close_temp = close_temp[~np.isnan(close_temp)]
        y = close_temp.reshape((len(close_temp), -1))
        coef = np.linalg.inv(x.T.dot(x)).dot(x.T).dot(y)
        y_hat = x.dot(coef)
        
        return abs(np.mean(y[-5:, 0]) - np.mean(y_hat[-5:, 0]))