from future_factor import FutureFactor
import pandas as pd
import numpy as np
import bottleneck as bk

class wyc_ts103_MinHigh_spot_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['high']} 
    normalize_size = 1000
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        high = data['high_000300.SH'][-50:].values
        f1 = bk.move_min(high, 10, min_count = 5) - bk.move_min(high, 25, min_count = 12)
        f2 = bk.move_min(high, 20, min_count = 10) - bk.move_min(high, 30, min_count = 15)
        f = np.nanmean((f1 - f2)[-20:])
        return f