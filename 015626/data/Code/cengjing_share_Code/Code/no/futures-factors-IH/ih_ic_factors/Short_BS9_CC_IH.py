import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_cc import *
from future_factor import FutureFactor


def r(data, x=np.nan):

    data[abs(data) < 1e-8] = x
    return data

    
class Short_BS9_CC_IH(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['amount', 'buy_superorder_count', 'buy_bigorder_count', 'buy_midorder_count', 'buy_smallorder_count']
    normalize_size = 1200 
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False

    def calculate(self, data):
        stk_amount = data['amount'].values[-65:]
        stk_buy_superorder_count = data['buy_superorder_count'].fillna(0).values[-65:]
        stk_buy_bigorder_count = data['buy_bigorder_count'].fillna(0).values[-65:]
        stk_buy_midorder_count = data['buy_midorder_count'].fillna(0).values[-65:]
        stk_buy_smallorder_count = data['buy_smallorder_count'].fillna(0).values[-65:]

        amount_sum = bk.move_sum(stk_amount, window=60, min_count=15, axis=0)
        amount_mask = np.nanquantile(amount_sum, 0.9, axis=1)
        amount_mask = np.expand_dims(amount_mask, axis=-1)
        alll = r(stk_buy_superorder_count + stk_buy_bigorder_count + stk_buy_midorder_count + stk_buy_smallorder_count)
        temp2 = (stk_buy_superorder_count + stk_buy_bigorder_count) / alll
        temp2_after_mask = ma.array(temp2, mask=(amount_sum<=amount_mask))
        factor_raw = np.nanmean(temp2_after_mask, axis=1)
        factor_mean = bk.move_mean(factor_raw, window=5, min_count=1, axis=0)
        return factor_mean[-1]