from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class dpo_std_zsj(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close']}
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '(-0.5,1]'
    handle_preadj = None 

    def calculate(self, data):
        close = data[['close_cont_IC']][-1298:]
        mma = bk.move_mean(close, 45, 22, axis = 0)[45:]
        dpo_raw = close[68:] - mma[:-23]
        dpo_std_raw = bk.move_std(dpo_raw, 30, 1, axis = 0)[-1200:]
        factor = bk.move_rank(dpo_std_raw, 1200, 1080, axis = 0)[-1]
        return factor