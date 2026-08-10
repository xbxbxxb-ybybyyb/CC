import numpy as np
from future_factor import FutureFactor
import bottleneck as bn

class MinuteIndexHLWeightIlliqDiff_IH(FutureFactor):
    '''
    Description: cs_mean(where(weight_rank > 0.9, illiq, nan)) - cs_mean(where(weight_rank <= 0.1, illiq, nan)), 
                where weight_rank = cs_rank(weight), illiq(abs(ret) / amount_ratio),
                ret = pct_chg(close, 30), amount_ratio = (amount,30) / ts_mean(amount, last 5 days)
    Class: Group_Stat
    Author: lixr, modified by lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 6
    data_dict = dict()
    data_dict['Stock'] = ['weight','close', 'amount']
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        threshold = 0.9
        n = 30
        weight = data['weight'].values[-1]
        weight_rank = bn.rankdata(weight) / len(weight)
        close_price = data['close'].values
        close_price[close_price == 0] = np.nan
        amount = data['amount'].values
        amount[amount == 0] = np.nan
        
        ret = (close_price[-n:] - close_price[-(n + 1):-1]) / close_price[-(n + 1):-1]
        amount_ratio = amount[-n:] / np.nanmean(amount[-(n + 237*5):-n], axis = 0)
        illiq = np.nanmean(abs(ret) / amount_ratio, axis = 0)
        factor_value = np.nanmean(illiq[weight_rank > threshold]) - np.nanmean(illiq[weight_rank <= (1 - threshold)])
        
        if np.isnan(factor_value) or np.isinf(factor_value):
            return 0
        else:
            return factor_value