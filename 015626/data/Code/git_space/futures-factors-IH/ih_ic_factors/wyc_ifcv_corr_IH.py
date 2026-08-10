from future_factor import FutureFactor
import numpy as np
import bottleneck as bk

def get_norm(fa):
    fmax = np.nanmax(fa)
    fmin = np.nanmin(fa)
    divisor = fmax - fmin
    if divisor < 1e-8:
        divisior = np.nan
    return ((fa[-1] - fmin)/ divisor) * 2 - 1

class wyc_ifcv_corr_IH(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IH':['close','volume']} 
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 

    def calculate(self, df):
        volume = df['volume_cont_IH'][-5*242 - 60:]
        close = df['close_cont_IH'][-5*242 - 60:]
        s = volume.rolling(30, min_periods=15).std()
        f = close.rolling(30, min_periods=15).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        factor = volume.rolling(30, min_periods=15).cov(close) / (s * f)
        factor = -1 * bk.move_mean(factor.values, 30, 15, axis = 0)
        factor = get_norm(factor[-5*242:])
        return factor