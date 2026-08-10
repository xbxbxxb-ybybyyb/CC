from future_factor import FutureFactor
import pandas as pd
import numpy as np
import bottleneck as bk

class a_to_osa_ic(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 0
    data_dict = dict()
    data_dict['Stock'] = ['amount','sell_lo_amount']
    normalize_size = 0
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.75,1]'
    handle_preadj = False

    def calculate(self, df):
        divnum = df['sell_lo_amount'].iloc[-1].sum()
        if divnum == 0:
            return np.nan
        else:
            return df['amount'].iloc[-1].sum() / divnum