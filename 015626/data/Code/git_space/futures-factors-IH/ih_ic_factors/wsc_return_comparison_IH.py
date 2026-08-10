import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

class wsc_return_comparison_IH(FutureFactor):

    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close'],'000016.SH':['close']}    
    normalize_size = 1200
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    handle_preadj = None 
    
    def calculate(self, data):
        a = data['close_000905.SH'][-193:].values
        b = data['close_000016.SH'][-193:].values
        a = a[3:] / a[:-3] - 1
        b = b[3:] / b[:-3] - 1
        c = a - b
        c[c > 0] = 1
        c[c <= 0] = 0
        temp = bk.move_sum(c, 180, min_count=90, axis = 0)
        temp[abs(temp)<1e-8] = np.nan
        factor = bk.move_sum(c, 30, min_count=15, axis = 0) / temp
        factor = np.nanmean(factor[-10:])
        return factor