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


class wsc_fast18_hf_IH(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'BuyTradeMoney']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False

    def calculate(self, data):
        stk_close = data['close'].values[-17:]
        stk_BuyTradeMoney = data['BuyTradeMoney'].fillna(0).values[-17:]

        x = section_rank_bk(stk_BuyTradeMoney, pct=True) * 2 - 1
        stk_ret = ts_pct_change(stk_close, 1)
        factor_raw = np.nansum(x * stk_ret, axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        return factor_mean[-1]