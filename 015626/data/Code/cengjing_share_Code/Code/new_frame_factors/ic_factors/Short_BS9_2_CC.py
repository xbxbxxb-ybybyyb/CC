import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd
import scipy


class Short_BS9_2_CC(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Stock'] = ['close','buy_superorder_count','buy_bigorder_count','buy_midorder_count','buy_smallorder_count']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = False

    def calculate(self, data):
        index_close = data['close_000905.SH'][-1203:]
        stk_close = data['close'][-1203:]
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.iloc[-1200:].corrwith(index_ret.iloc[-1200:,0])
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        bool_df = stk_index_corr[stk_index_corr>stk_index_corr.quantile(0.9)]
        bool_stk_list = bool_df.index.to_list()
        
        a = data['buy_superorder_count'][-5:].fillna(0) + data['buy_bigorder_count'][-5:].fillna(0) + data['buy_midorder_count'][-5:].fillna(0) + data['buy_smallorder_count'][-5:].fillna(0)
        temp2 = (data['buy_bigorder_count'][-5:].fillna(0) + data['buy_superorder_count'][-5:].fillna(0))/ a.replace(0, np.nan)
        temp2 = temp2.replace([-np.inf, np.inf], np.nan)
        factor = np.nanmean(temp2[bool_stk_list].values,axis = 1)
        factor = np.nanmean(factor)
        
        return factor