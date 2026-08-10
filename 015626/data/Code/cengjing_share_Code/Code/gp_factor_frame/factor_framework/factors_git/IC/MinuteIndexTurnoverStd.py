from future_factor import FutureFactor
import numpy as np
from scipy.stats import skew


class MinuteIndexTurnoverStd(FutureFactor):
    '''
    Description: std(amount_000905.SH, 20)
    Class: Liquidity
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    days_past = 1
    data_dict = {}
    data_dict['Index_Id'] = {'000905.SH': ['amount']}
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):        
        amount = data['amount_000905.SH'].values[-20:]
        f = np.std(amount)
        return f
