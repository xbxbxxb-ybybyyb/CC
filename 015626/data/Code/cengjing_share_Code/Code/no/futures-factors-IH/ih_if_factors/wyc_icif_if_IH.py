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

class wyc_icif_if_IH(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close'],'IH':['close']} 
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[0,1]'
    handle_preadj = None 
 
    def calculate(self, df):
        factor = (df['close_cont_IC'] - df['close_cont_IH'])[-1290:].values
        factor = factor - bk.move_mean(factor, 60, min_count = 30, axis = 0)
        factor = bk.move_mean(factor, 20, min_count = 10, axis = 0)
        factor = get_norm(factor[-5*242:])
        return factor

