import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd
import scipy


class Short_GA_CFG_2_CC(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Stock'] = ['close','adjfactor','open','high','low']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 240
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        index_close = data['close_000905.SH'][-1203:]
        stk_close = data['close_preadj'][-1203:]
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.iloc[-1200:].corrwith(index_ret.iloc[-1200:,0])
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        bool_df = stk_index_corr[stk_index_corr>stk_index_corr.quantile(0.95)]
        bool_stk_list = bool_df.index.to_list()
        
        high = data['high_preadj'][-31:]
        close = data['close_preadj'][-31:]
        opendf = data['open_preadj'][-31:]
        low = data['low_preadj'][-31:]
        a = high.rolling(30, min_periods = 15).max()-opendf.shift(30)
        b = close - low.rolling(30, min_periods = 15).min()
        c = (high.rolling(30, min_periods = 15).max()-low.rolling(30, min_periods = 15).min())*2
        vwtc_r = (a[-1:]+b[-1:])/c[-1:]
        vwtc_r = vwtc_r.replace([-np.inf, np.inf], np.nan)
        factor = np.nanmean(vwtc_r[bool_stk_list].values)
        return factor