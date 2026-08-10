import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_wsc_1_0 import *
from future_factor import FutureFactor


class LminLmean_nr_cv_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 6
    data_dict = dict()
    data_dict['Stock'] = ['close', 'low', 'stk_index_corr_hs300', 'adjfactor']
    normalize_size = 720
    normalize_type = 'ts_rank' 
    
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-1275:]
        stk_low = data['low_preadj'].values[-1275:]
        stk_index_corr_hs300 = data['stk_index_corr_hs300'].values[-1275:]

        stk_ret = ts_pct_change(stk_close, 1)
        stk_vol = ts_std(stk_ret, 30)
        mask1 = np.nanquantile(stk_index_corr_hs300, 0.8, axis=1)
        mask1 = np.expand_dims(mask1, axis=-1)
        mask2 = np.nanquantile(stk_vol, 0.8, axis=1)
        mask2 = np.expand_dims(mask2, axis=-1)
        ctl_r = -bk.move_min(stk_low, 60, 15, axis=0) / bk.move_mean(stk_low, 30, 10, axis=0)
        ctl_r = rolling_norm(ctl_r, 242*5)
        tempdf = ma.array(ctl_r, mask=((stk_index_corr_hs300<=mask1)|(stk_vol<=mask2)))
        tempdf = np.nansum(tempdf, axis=1)
        factor = bk.move_mean(tempdf, 5, 2)
        return factor[-1]