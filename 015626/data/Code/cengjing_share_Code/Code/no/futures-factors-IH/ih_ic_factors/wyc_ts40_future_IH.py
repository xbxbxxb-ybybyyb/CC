from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

def get_norm(fa):
    fmax = np.nanmax(fa)
    fmin = np.nanmin(fa)
    divisor = fmax - fmin
    if divisor < 1e-8:
        divisior = np.nan
    return ((fa[-1] - fmin)/ divisor) * 2 - 1

class wyc_ts40_future_IH(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IH':['close', 'vwap']}
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 
    
    def calculate(self, df):
        vwap = df['vwap_cont_IH'][-1410:]
        
        close_s20 = df['close_cont_IH'].shift(20)[-1410:]
        s = vwap.rolling(60, min_periods=30).std()
        f = close_s20.rolling(60, min_periods=30).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        aa = vwap.rolling(20, min_periods=10).cov(close_s20) / (s * f)
        
        close = df['close_cont_IH'][-1350:]
        ctemp = (bk.move_sum(close, 20, 10, axis = 0) / 20) - close
        
        factor = ctemp[-1330:] + aa[-1330:]
        factor = bk.move_rank(factor, 20, 10, axis = 0)[-1310:]
        factor = bk.move_mean(factor, 100, 50, axis = 0)[-1210:]
        factor = get_norm(factor)

        return factor