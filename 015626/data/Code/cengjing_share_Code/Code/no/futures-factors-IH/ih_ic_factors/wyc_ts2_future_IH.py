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

def get_delta(data, n):
    return data[n:] - data[:-n]

class wyc_ts2_future_IH(FutureFactor):
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
        volume = df['volume_cont_IH'].values[-5*242 - 17:]
        close = df['close_cont_IH'].values[-5*242 - 17:]
        dev = get_delta(volume, 5)
        dev[dev > 0] = 1
        dev[dev < 0] = -1
        factor = -1 * dev * get_delta(close, 5)
        
        factor = bk.move_mean(factor,2,1,axis = 0)
        factor = bk.move_mean(factor,10,5,axis = 0)
        factor = get_norm(factor[-5*242:])
        return factor