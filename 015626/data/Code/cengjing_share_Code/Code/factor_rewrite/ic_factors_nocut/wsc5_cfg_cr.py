import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc5_cfg_cr(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'stk_index_corr_zz500', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '(-0.8,1]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-56:]
        stk_index_corr = data['stk_index_corr_zz500'].values[-56:]
        stk_index_corr_rank_mask = 2 * section_rank_np(stk_index_corr, pct=True) - 1
        n = 20
        m = int(n/2) + 1
        close_ma = ts_mean(stk_close, n)
        dev = stk_close - close_ma
        devpos = dev.copy()
        devneg = -dev.copy()
        devpos[devpos<0] = 0
        devneg[devneg<0] = 0
        sumpos = ts_sum(devpos, m)
        sumneg = ts_sum(devneg, m)
        temp = replace_zero(sumpos + sumneg)
        tii = sumpos / temp
        factor_raw = np.nansum(tii * stk_index_corr_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 25)
        return factor_mean[-1]
