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

class wyc_if_2hour_return(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['close']} 
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '[0,1]'
    handle_preadj = None 

    def calculate(self, df):
        cif = df['close_cont_IF'].values
        ifreturn = cif[1:] / cif[:-1] - 1
        factor = bk.move_mean(ifreturn, 200, min_count=100, axis = 0)
        factor = get_norm(factor[-5 * 242:])
        return factor