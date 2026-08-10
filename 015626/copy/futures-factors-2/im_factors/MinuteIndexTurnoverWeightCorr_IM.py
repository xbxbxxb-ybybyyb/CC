from future_factor import FutureFactor
import numpy as np


class MinuteIndexTurnoverWeightCorr_IM(FutureFactor):
    '''
    Description: ts_mean(cs_corr(amount, weight), 10)
    Class: Liq_Cs_Stat
    Author: jinpx, modified by hefj
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['amount', 'weight']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):        
        amount = data['amount'].values[-10:]
        amount[amount == 0] = np.nan
        weight = data['weight'].values[-1]
        corr = []
        for j in range(1, 11):
            valid = np.logical_and(~np.isnan(amount[-j]), ~np.isnan(weight))
            c = np.corrcoef(amount[-j][valid], weight[valid])[0, 1]
            if np.isnan(c):
                c = 0
            corr = np.append(corr, c)
        f = np.nanmean(corr)
        return f
