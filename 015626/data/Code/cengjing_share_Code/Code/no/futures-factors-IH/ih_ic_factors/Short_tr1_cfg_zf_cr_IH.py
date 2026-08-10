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


class Short_tr1_cfg_zf_cr_IH(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = ['close', 'high', 'low', 'stk_index_corr_sh50', 'adjfactor']
    normalize_size = 1210
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_high = data['high_preadj'].values[-362:]
        stk_low = data['low_preadj'].values[-362:]
        stk_close = data['close_preadj'].values[-362:]
        stk_index_corr_zz500 = data['stk_index_corr_sh50'].values[-362:]
        
        hh = ts_max(stk_high, 120)
        ll = ts_min(stk_low, 120)
        fac = 2 * stk_close / (hh + ll)
        facorg = rolling_norm(fac, 242)
        cr = section_rank_bk(stk_index_corr_zz500, pct=True) * 2 - 1
        fac = np.nansum(facorg * cr, axis=1)
        return fac[-1]