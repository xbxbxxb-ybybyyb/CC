from future_factor import FutureFactor
import pandas as pd
import numpy as np
import bottleneck as bk
import numpy.ma as ma

class wyc_ts108_HLAmplitude_spot_IF_IM(FutureFactor):
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000852.SH':['close','high','low']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        N = 20
        v = data['high_000852.SH'][-N:].values - data['low_000852.SH'][-N:].values
        c = data['close_000852.SH'][-N:].values
        v_high = ma.array(v, mask = (c <= np.quantile(c, 0.75)))
        v_low = ma.array(v, mask = (c >= np.quantile(c, 0.25)))
        v_high_mean = np.nanmean(list(v_high))
        v_low_mean = np.nanmean(list(v_low)) # 此因子要注意v_low中取不到值的情况，即v_low有可能为[-,-,-,-,-]，用list包起来后可得结果nan，否则报错
        factor = v_high_mean - v_low_mean
        return factor * -1