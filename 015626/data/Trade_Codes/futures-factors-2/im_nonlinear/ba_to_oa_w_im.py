from future_factor import FutureFactor
import pandas as pd
import numpy as np
import bottleneck as bk

class ba_to_oa_w_im(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 0
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeMoney','lo_amount','weight']
    normalize_size = 0
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.75,1]'
    handle_preadj = False

    def calculate(self, df):
        return ((df['BuyTradeMoney'].iloc[-1] / df['lo_amount'].iloc[-1]).replace([np.inf,-np.inf], np.nan) * df['weight'].iloc[-1]).sum()