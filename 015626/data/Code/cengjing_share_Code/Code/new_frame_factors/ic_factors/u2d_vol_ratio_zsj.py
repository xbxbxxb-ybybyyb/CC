import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

class u2d_vol_ratio_zsj(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close','adjfactor','volume']
    normalize_size = 242*3
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        stk_close = data['close_preadj'][-91:]
        stk_volume = data['volume_preadj'][-90:]
        stk_ret = (stk_close / stk_close.shift(1) - 1)[-90:]
        up_mask = stk_ret > 0
        down_mask = stk_ret < 0

        up_vol = stk_volume[up_mask].sum(axis=1)
        down_vol = stk_volume[down_mask].sum(axis=1)
        down_vol[abs(down_vol)<1e-8] = np.nan
        u2d_vol_ratio_raw = up_vol / down_vol
        factor = np.nanmean(u2d_vol_ratio_raw)

        return factor