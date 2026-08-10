import numpy as np
import pandas as pd
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


class wsc_spot_9_if_IH(FutureFactor):
    """
    过去20分钟里，沪深300涨幅最高的5分钟的平均收益率
    """
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        spot_close = data['close_000016.SH'].iloc[-37:]
        factor_raw = pd.Series(np.nan, index=spot_close.index)
        
        n = 20
        ret1 = ts_pct_change(spot_close, 1)
        ret1_expanding = rolling_window_upgrade(ret1.values, n).copy()
        ret1_sort = np.argsort(ret1_expanding, axis=1)
        ret1_expanding[ret1_sort<n-5] = np.nan
        factor_raw[n-1:] = np.nanmean(ret1_expanding, axis=1)
        factor = np.nanmean(factor_raw[-15:])
        return factor
