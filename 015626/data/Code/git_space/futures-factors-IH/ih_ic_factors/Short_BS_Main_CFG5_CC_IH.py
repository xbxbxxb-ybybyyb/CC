import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_cc import *
from operators_wsc_1_0 import *
from future_factor import FutureFactor


def ts_truncated_ema_1(data, d, alpha):
    # truncated ema
    if (alpha >= 1) or (alpha <= 0):
        raise ValueError('`alpha` must be in (0, 1)')
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    return ts_decay_linear(data=data, d=d, weight=weight)


def ts_truncated_ema_span_1(data, d, span):
    # truncated ema
    return ts_truncated_ema_1(data=data, d=d, alpha=2 / (span + 1))


class Short_BS_Main_CFG5_CC_IH(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_midorder_count', 'buy_smallorder_count', 'weight', 'close']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False

    def calculate(self, data):
        stk_close = data['close'].values[-127:]
        stk_weight = data['weight'].values[-127:]
        skt_buy_midorder_count = data['buy_midorder_count'].fillna(0).values[-127:]
        stk_buy_smallorder_count = data['buy_smallorder_count'].fillna(0).values[-127:]
        
        
        df_s = bk.move_sum(skt_buy_midorder_count + stk_buy_smallorder_count, 5, 2, axis=0) * stk_weight
        df_s[stk_weight <= 0] = np.nan
        hret = ts_pct_change(stk_close, 1)
        hret = ts_truncated_ema_span_1(hret, 120, 20)
        df_s_mask = np.nanmedian(df_s, axis=1)
        df_s_mask = np.expand_dims(df_s_mask, axis=-1)
        hret_1 = ma.array(hret, mask=(df_s<=df_s_mask))
        hret_2 = ma.array(hret, mask=(df_s>=df_s_mask))
        temp2 = np.nanmean(hret_1, axis=1) - np.nanmean(hret_2, axis=1)
        return temp2[-1]