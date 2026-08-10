import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc9_cfg_wr(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['volume', 'close', 'open', 'weight', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_open = data['open_preadj'].values[-51:]
        stk_close = data['close_preadj'].values[-51:]
        stk_volume = data['volume_preadj'].values[-51:]
        stk_weight = data['weight'].iloc[-51:]
        # weight_rank_mask = section_rank_np(stk_weight, pct=True) * 2 - 1
        weight_rank_mask = stk_weight.rank(axis=1, pct=True) * 2 - 1
        min_30_earning = (stk_close - ts_delay(stk_open, 30)) * stk_volume
        # print(min_30_earning.shape, weight_rank_mask.values.shape)
        factor_raw = np.nansum(min_30_earning * weight_rank_mask.values, axis=1)
        factor_mean = ts_mean(factor_raw, 20)
        return factor_mean[-1]
