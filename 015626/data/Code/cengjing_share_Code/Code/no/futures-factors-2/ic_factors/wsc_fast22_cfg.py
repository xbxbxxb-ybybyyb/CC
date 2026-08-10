import numpy as np
import bottleneck as bk
from operators_wsc_1_0 import *
from help_functions_wsc import *
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


class wsc_fast22_cfg(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'stk_index_corr_zz500', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-102:]
        stk_index_corr = data['stk_index_corr_zz500'].values[-102:]
        stk_index_corr_rank_mask = section_rank_bk(stk_index_corr, pct=True) * 2 - 1

        n = 10
        temp = replace_zero(ts_sum(abs(ts_delta(stk_close, 1)), n))
        vi = abs(ts_delta(stk_close, n)) / temp
        vidya = vi * stk_close + (1-vi) * ts_delay(stk_close, 1)
        factor_init = rolling_norm(vidya, 90)
        factor_raw = np.nansum(factor_init * stk_index_corr_rank_mask, axis=1)
        return factor_raw[-1]