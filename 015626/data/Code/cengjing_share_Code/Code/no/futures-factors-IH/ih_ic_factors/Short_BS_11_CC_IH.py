import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_cc import *
from future_factor import FutureFactor


def r(data, x=np.nan):

    data[abs(data) < 1e-8] = x
    return data

    
class Short_BS_11_CC_IH(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = ['amount', 'close', 'open', 'PxVolCorr', 'AbsPxPath']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-334:]
        stk_close = data['close'].values[-334:]
        stk_open = data['open'].values[-334:]
        stk_PxVolCorr = data['PxVolCorr'].values[-334:]
        stk_AbsPxPath = data['AbsPxPath'].values[-334:]

        df_s = bk.move_sum(stk_amount, 30, 15, axis=0)
        amount_mask = np.nanquantile(df_s, 0.9, axis=1)
        amount_mask = np.expand_dims(amount_mask, axis=-1)
        sig1 = ma.array(stk_PxVolCorr, mask=(df_s<=amount_mask))
        sig1 = np.nanmean(sig1, axis=1)
        sig1 = bk.move_rank(sig1, 300, 150)
        sig2 = ma.array((stk_close - stk_open) / r(stk_AbsPxPath), mask=(df_s<=amount_mask))
        sig2 = np.nanmean(sig2, axis=1)
        sig2 = bk.move_rank(sig2, 300, 150)
        sig = sig1 + sig2
        factor_mean = bk.move_mean(sig, 4, 2)
        return factor_mean[-1]