from future_factor import FutureFactor
import pandas as pd
import numpy as np
import bottleneck as bk

class wyc_ts105_MinLowStd_spot_IF_IM(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000852.SH':['low']} 
    normalize_size = 1000
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        temp = data['low_000852.SH'][-65:].values
        f1 = bk.move_min(temp, 10, min_count = 5) - bk.move_min(temp, 20, min_count = 10)
        f2 = bk.move_min(temp, 20, min_count = 10) - bk.move_min(temp, 50, min_count = 25)
        f = np.nanstd((f1 - f2)[-15:], ddof = 1)
        return f