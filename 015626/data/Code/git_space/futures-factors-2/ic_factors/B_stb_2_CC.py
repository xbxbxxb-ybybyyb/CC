from operators_wsc_1_0 import *
import numpy.ma as ma
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


def ts_truncated_ema_1(data, d, alpha):
    # truncated ema
    if (alpha >= 1) or (alpha <= 0):
        raise ValueError('`alpha` must be in (0, 1)')
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    return ts_decay_linear(data=data, d=d, weight=weight)


def ts_truncated_ema_span_1(data, d, span):
    # truncated ema
    return ts_truncated_ema_1(data=data, d=d, alpha=2 / (span + 1))


class B_stb_2_CC(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [ 'buy_smallorder_volume_thismin', 'buy_bigorder_volume_thismin', 'amount', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        
        amount1 = data['amount'].values[-120:]
        amount_sum = amount1.sum(axis = 0)
        
        amount_mask = np.nanquantile(amount_sum, 0.9)
        amount_mask = np.expand_dims(amount_mask, axis=-1)
        
        temp1 = data['buy_smallorder_volume_thismin'].values[-20:]
        temp2 = data['buy_bigorder_volume_thismin'].values[-20:]
            
        df_s1 = np.nanmean(temp1, axis = 0)
        df_s2 =  np.nanmean(temp2, axis = 0)
        
        factor_raw = data['weight'].values[-1] * df_s1 / r(df_s2)

        factor_raw_after_mask = ma.array(factor_raw, mask=(amount_sum<=amount_mask))
        factor = np.nanmean(factor_raw_after_mask)
        
        
        return -factor

