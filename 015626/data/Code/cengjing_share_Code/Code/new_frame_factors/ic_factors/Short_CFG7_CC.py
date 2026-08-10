import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_cc import *
from operators_wsc_1_0 import ts_pct_change
from future_factor import FutureFactor

def r(data, x=np.nan):

    data[abs(data) < 1e-8] = x
    return data

    
class Short_CFG7_CC(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['turnover_rate', 'close', 'open', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        stk_close = data['close_preadj'].values[-82:]
        stk_open = data['open_preadj'].values[-82:]
        stk_turnover = data['turnover_rate'].values[-82:]
        
        ret = stk_close / stk_open - 1
        hret = ts_pct_change(stk_close, 1)
        stk_turnover[stk_close >= stk_open] = np.nan
        ret[stk_close >= stk_open] = np.nan
        cc1 = stk_turnover / r(abs(ret))
        ccc1 = bk.move_mean(cc1, 60, 7, axis=0)
        ccc1_mask = np.expand_dims(np.nanmedian(ccc1, axis=1), axis=-1)
        hret1 = ma.array(hret, mask=(ccc1<=ccc1_mask))
        hret2 = ma.array(hret, mask=(ccc1>=ccc1_mask))
        cc2 = np.nanmean(hret1, axis=1) - np.nanmean(hret2, axis=1)
        ccc2 = bk.move_mean(cc2, 20, 10)
        return ccc2[-1]