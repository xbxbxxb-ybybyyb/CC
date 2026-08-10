from future_factor import FutureFactor
import pandas as pd
import numpy as np
import bottleneck as bk

class wyc_ts106_5DaysRet_spot_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 5
    data_dict = {}
    data_dict['Index_Id'] = {'000300.SH': ['close']}
    normalize_size = 200
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        N = 5
        temp = data['close_000300.SH'].values[-N * 237:].reshape(N, -1)[:,-1]
        temp_ratio = temp[1:] / temp[:-1] - 1
        f = np.nanmean(temp_ratio)
        return f