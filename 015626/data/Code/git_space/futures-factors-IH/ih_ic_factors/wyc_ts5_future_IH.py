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
    
class wyc_ts5_future_IH(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 11
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IH':['close']} 
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.75,1]'
    handle_preadj = None 

    def calculate(self, df):
        N = 45
        close = df['close_cont_IH'].values
        origin = get_delta((bk.move_sum(close, N,int(N/2), axis =0) / N), N) / close[:-N]
        change1 = -1 * (close - bk.move_min(close, N,int(N/2), axis =0))[N:]
        change2 = -1 * get_delta(close, 3)[N-3:]
        factor = np.where(origin<=0.05,change1,change2)[-1200 - 15 - 5*242:]
        factor = bk.move_rank(-1*factor, 1200, 600, axis = 0)[-5*242 - 15:]
        factor = bk.move_mean(factor,15,7,axis = 0)

        factor = get_norm(factor[-5*242:])
        return factor