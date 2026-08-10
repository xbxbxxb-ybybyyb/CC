import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_cc import *
from operators_wsc_1_0 import ts_pct_change
from future_factor import FutureFactor


class Short_CFG16_CC(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 6
    data_dict = dict()
    data_dict['Stock'] = ['close', 'low', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-1296:]
        stk_low = data['low_preadj'].values[-1296:]
        
        hret = ts_pct_change(stk_close, 1)
        i1 = -bk.move_min(stk_low, 90, 15, axis=0) / bk.move_mean(stk_low, 60, 10, axis=0)
        i1_mask = np.nanmedian(i1, axis=1)
        i1_mask = np.expand_dims(i1_mask, axis=-1)
        hret_up_after_mask = ma.array(hret, mask=(i1<=i1_mask))
        hret_down_after_mask = ma.array(hret, mask=(i1>=i1_mask))
        i2 = np.nanmean(hret_up_after_mask, axis=1) - np.nanmean(hret_down_after_mask, axis=1)
        i2 = bk.move_rank(i2, 1200, 600)
        i2 = bk.move_mean(i2, 6, 2)
        return i2[-1]