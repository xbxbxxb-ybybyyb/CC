import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_cc import *
from future_factor import FutureFactor


def r(data, x=np.nan):

    data[abs(data) < 1e-8] = x
    return data

    
def section_rank_bk(data, pct=False):
    # numpy的argsort函数在值相同的情况下会出现排序不稳定的情况，所以用bk.rankdata代替，对应df.rank(method='first')
    if not isinstance(data, np.ndarray):
        raise TypeError('Only supports the following type: np.ndarray')
    data_argsort = bk.rankdata(data, axis=1)  # +1是因为numpy从0计数，pandas从1计数
    data_argsort[np.isnan(data)] = np.nan  # numpy argsort会让nan也参与排序，但是pandas不会，所以把这些值重新置为nan
    if pct == True:
        data_argsort = data_argsort / (~np.isnan(data)).sum(axis=1, keepdims=True)
    return data_argsort


class Short_SYXWR_ar_CFG_CC(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['amount', 'open', 'close', 'low', 'high', 'adjfactor']
    normalize_size = 1200 
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        stk_amount = data['amount'].values[-35:]
        stk_close = data['close_preadj'].values[-35:]
        stk_open = data['open_preadj'].values[-35:]
        stk_high = data['high_preadj'].values[-35:]
        stk_low = data['low_preadj'].values[-35:]
        
        stk_amount_rank = section_rank_bk(stk_amount, pct=True) * 2 - 1
        temp1 = np.where(stk_open > stk_close, stk_open, stk_close)
        t_pcor = (stk_high - temp1) / r(bk.move_mean(stk_high - temp1, 30, 15, axis=0))
        t_pcor2 = (stk_close - bk.move_min(stk_low, 30, 15, axis=0)) / r(bk.move_max(stk_high, 30, 15, axis=0) - bk.move_min(stk_low, 30, 15, axis=0))
        t_pcorr = (t_pcor2 - t_pcor)
        factor = np.nansum(t_pcorr * stk_amount_rank, axis=1)
        factor = bk.move_mean(factor, 5, 2)
        return factor[-1]