import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_cc import *
from operators_wsc_1_0 import ts_pct_change
from future_factor import FutureFactor


class Short_updown_cfg2_CC(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['amount', 'close', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        stk_close = data['close_preadj'].values[-150:]
        stk_amount = data['amount'].values[-150:]
        
        df_s = bk.move_sum(stk_amount, 120, 15, axis=0)
        amount_mask = np.nanquantile(df_s, 0.9, axis=1)
        amount_mask = np.expand_dims(amount_mask, axis=-1)
        amount_after_mask = (df_s > amount_mask)
        hclose = ts_pct_change(stk_close, 1)
        up_close = ma.array(amount_after_mask, mask=(hclose<=0))
        up_close = np.nansum(up_close, axis=1)
        down_close = ma.array(amount_after_mask, mask=(hclose>=0))
        down_close = np.nansum(down_close, axis=1)
        vwtc_r = (up_close - down_close) / (up_close + down_close)
        vwtc_r = bk.move_mean(vwtc_r, 30, 5)
        return vwtc_r[-1]