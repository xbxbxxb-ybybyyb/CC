import numpy as np
import bottleneck as bk
from operators_wsc_1_0 import *
from future_factor import FutureFactor


def section_rank_bk(data, pct=False):
    # numpy的argsort函数在值相同的情况下会出现排序不稳定的情况，所以用bk.rankdata代替，对应df.rank(method='first')
    if not isinstance(data, np.ndarray):
        raise TypeError('Only supports the following type: np.ndarray')
    data_argsort = bk.rankdata(data, axis=1)  # +1是因为numpy从0计数，pandas从1计数
    data_argsort[np.isnan(data)] = np.nan  # numpy argsort会让nan也参与排序，但是pandas不会，所以把这些值重新置为nan
    if pct == True:
        data_argsort = data_argsort / (~np.isnan(data)).sum(axis=1, keepdims=True)
    return data_argsort


class Short_ss1_cfg_zf(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 6
    data_dict = dict()
    data_dict['Stock'] = ['close', 'high', 'amount', 'adjfactor']
    normalize_size = 1210
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-1272:]
        stk_close = data['close_preadj'].values[-1272:]
        stk_high = data['high_preadj'].values[-1272:]
        
        rtn = ts_pct_change(stk_close, 1)
        vol = ts_std(rtn, 60)
        vol[vol<1e-8]=0
        vol[vol == 0] = np.nan
        ret = stk_close / ts_max(ts_delay(stk_high, 1), 60) - 1
        factorg = rolling_norm(ret / vol, 1210)
        ar = section_rank_bk(stk_amount, pct=True) * 2 - 1
        fac = np.nansum(factorg * ar, axis=1)
        return fac[-1]