from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class csv_disp_sign_zsj_IH(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'adjfactor'] 
    normalize_size = 1210
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        stk_close = data['close_preadj'][-131:]
        stk_ret = (stk_close / stk_close.shift(1) - 1)
        csv_disp = stk_ret.std(axis=1)
        stk2idx_ret = stk_ret.mean(axis=1)
        csv_disp_sign_raw = csv_disp * np.sign(stk2idx_ret)
        factor = np.nanmean(csv_disp_sign_raw[-130:].values)
        return factor