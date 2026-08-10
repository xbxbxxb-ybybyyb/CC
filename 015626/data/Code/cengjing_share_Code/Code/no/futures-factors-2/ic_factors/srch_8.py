from operators_wsc_1_0 import *
import numpy.ma as ma
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


def ts_truncated_ema_1(data, d, alpha):
    # truncated ema
    if (alpha >= 1) or (alpha <= 0):
        raise ValueError('`alpha` must be in (0, 1)')
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    return ts_decay_linear(data=data, d=d, weight=weight)


def ts_truncated_ema_span_1(data, d, span):
    # truncated ema
    return ts_truncated_ema_1(data=data, d=d, alpha=2 / (span + 1))


class srch_8(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'amount', 'sell_big_lo_counts', 'sell_lo_counts', 'sell_lo_amount', 'buy_smallorder_money']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):

        
        close = data['close'][-81:]     
        amount = data['amount'][-81:]
        ret_1min = close.diff(1) / close.shift(1)
        ra_corr = ret_1min.corrwith(amount, axis = 1)
        
        
        a = data['sell_big_lo_counts'].values[-142:]
        b = data['sell_lo_counts'].values[-142:]
        bosn_2_to_osn = np.nansum(a, axis = 1) / np.nansum(b, axis = 1)
        
        sell_lo_amount = data['sell_lo_amount'].values[-71:]
        sell_lo_counts = data['sell_lo_counts'].values[-71:]
        osa_to_osn = np.nansum(sell_lo_amount, axis = 1) / np.nansum(sell_lo_counts, axis = 1)
        
        buy_smallorder_money = data['buy_smallorder_money'].values[-71:]
        bba_4 = np.nansum(buy_smallorder_money, axis = 1)
        
        factor = min2(aroon(ra_corr, ts_argmin(bosn_2_to_osn, 60)[-81:], 80)[-1], ts_corr(osa_to_osn, bba_4, 70)[-1])
        return factor

