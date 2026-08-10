from future_factor import FutureFactor
import pandas as pd
import numpy as np
import bottleneck as bk

class a_to_osa_w_ic(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 0
    data_dict = dict()
    data_dict['Stock'] = ['amount','sell_lo_amount','weight']
    normalize_size = 0
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.75,1]'
    handle_preadj = False

    def calculate(self, df):
        return ((df['amount'].iloc[-1] / df['sell_lo_amount'].iloc[-1]).replace([np.inf,-np.inf], np.nan) * df['weight'].iloc[-1]).sum()