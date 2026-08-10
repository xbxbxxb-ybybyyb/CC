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

class wyc_icif(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close'],'IF':['close']} 
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 
 
    def calculate(self, df):
        factor = (df['close_cont_IC'] - df['close_cont_IF']).values
        factor = factor - bk.move_mean(factor, 240, min_count = 120, axis = 0)
        factor = bk.move_mean(factor, 20, min_count = 10, axis = 0)
        factor = get_norm(factor[-5*242:])
        return factor

