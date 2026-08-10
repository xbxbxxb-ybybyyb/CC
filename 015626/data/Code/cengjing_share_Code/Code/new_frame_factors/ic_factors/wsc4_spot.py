import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

class wsc4_spot(FutureFactor):

    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}    
    normalize_size = 1200
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    handle_preadj = None 
    
    def calculate(self, data):
        close = data['close_000905.SH'][-121:].values
        N = 20
        cmean = bk.move_mean(close, N, min_count=N//2, axis = 0)
        dpo = (close[11:] - cmean[:-11])[-90:]
        factor = abs(dpo - bk.move_median(dpo, 60, min_count=30, axis = 0))
        factor = np.nanmean(factor[-30:])
        return factor