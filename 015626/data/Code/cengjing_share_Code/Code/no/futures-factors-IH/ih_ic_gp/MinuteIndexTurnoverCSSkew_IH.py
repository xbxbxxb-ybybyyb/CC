from future_factor import FutureFactor
import numpy as np
from scipy.stats import skew


class MinuteIndexTurnoverCSSkew_IH(FutureFactor):
    '''
    Description: -ts_mean(cs_skew(amount), 15)
    Class: Liq_Cs_Stat
    Author: jinpx, modified by hefj
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['amount']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):        
        amount = data['amount'].values[-15:]
        amount[amount == 0] = np.nan
        f = -np.nanmean(skew(amount, axis=1, nan_policy='omit'))
        return f
