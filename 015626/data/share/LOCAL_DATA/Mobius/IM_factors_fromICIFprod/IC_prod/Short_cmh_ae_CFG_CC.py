import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_cc import *
from operators_wsc_1_0 import ts_pct_change
from future_factor import FutureFactor


class Short_cmh_ae_CFG_CC(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 6
    data_dict = dict()
    data_dict['Stock'] = ['amount', 'turnover_rate', 'close', 'high', 'adjfactor']
    normalize_size = 242
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        stk_close = data['close_preadj'].values[-1382:]
        stk_high = data['high_preadj'].values[-1382:]
        stk_amount = data['amount'].values[-1382:]
        stk_turnover = data['turnover_rate'].values[-1382:]
        
        df_s = bk.move_sum(stk_amount, 120, 15, axis=0)
        temp1 = np.nanquantile(df_s, 0.8, axis=1)
        temp1 = np.expand_dims(temp1, axis=-1)
        ret_30 = ts_pct_change(stk_turnover, 30)
        temp5 = np.nanquantile(ret_30, 0.8, axis=1)
        temp5 = np.expand_dims(temp5, axis=-1)
        vwtc_r = stk_high - bk.move_mean(stk_close, 180, 30, axis=0)
        vwtc_r_min = bk.move_min(vwtc_r, 1200, 600, axis=0)
        vwtc_r_max = bk.move_max(vwtc_r, 1200, 600, axis=0)
        vwtc_r = (vwtc_r - vwtc_r_min) / (vwtc_r_max - vwtc_r_min)
        factor = ma.array(vwtc_r, mask=(df_s<=temp1)|(ret_30<=temp5))
        factor = np.nanmean(factor, axis=1)
        factor = bk.move_mean(factor, 2, 1)
        return factor[-1]