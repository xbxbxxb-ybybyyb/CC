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

def rolling_norm(sig, window=1200, method='max_min'):
    assert isinstance(sig, pd.Series) or isinstance(sig, pd.DataFrame) or isinstance(sig, np.ndarray), 'input must be a series, dataframe or ndarray'
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            if isinstance(sig, pd.DataFrame):
                sig_max = pd.DataFrame(bk.move_max(sig, window=window, min_count=int(window / 2), axis=0),
                                       index=sig.index, columns=sig.columns)
                sig_min = pd.DataFrame(bk.move_min(sig, window=window, min_count=int(window / 2), axis=0),
                                       index=sig.index, columns=sig.columns)
                temp = sig_max - sig_min
                temp[abs(temp)<1e-8] = np.nan
                signal = (sig - sig_min) / temp
            elif isinstance(sig, pd.Series):
                sig_max = pd.Series(bk.move_max(sig, window=window, min_count=int(window / 2), axis=0),
                                   index=sig.index, name=sig.name)
                sig_min = pd.Series(bk.move_min(sig, window=window, min_count=int(window / 2), axis=0),
                                    index=sig.index, name=sig.name)
                temp = sig_max - sig_min
                temp[abs(temp)<1e-8] = np.nan
                signal = (sig - sig_min) / temp
            elif isinstance(sig, np.ndarray):
                sig_max = bk.move_max(sig, window=window, min_count=int(window / 2), axis=0)
                sig_min = bk.move_min(sig, window=window, min_count=int(window / 2), axis=0)
                temp = sig_max - sig_min
                temp[abs(temp)<1e-8] = np.nan
                signal = (sig - sig_min) / temp
            return 2 * signal - 1
        elif method == 'ts_rank':
            if isinstance(sig, pd.DataFrame):
                signal = pd.DataFrame(bk.move_rank(sig, window=window, min_count=int(window / 2), axis=0),
                                      index=sig.index, columns=sig.columns)
            elif isinstance(sig, pd.Series):
                signal = pd.Series(bk.move_rank(sig, window=window, min_count=int(window / 2), axis=0),
                                   index=sig.index, name=sig.name)
            elif isinstance(sig, np.ndarray):
                output = bk.move_rank(sig, window=d, min_count=int(d / 2), axis=0)
            return signal
        
        
class xdy_ts13_future(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 9
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['high']} 
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[0,1]'
    handle_preadj = None
    
    def calculate(self, df):
        high = df['high_cont_IC'][-2091:].values
        factor = bk.move_max(high, 121, 60, axis = 0)[-1970:]
        factor = rolling_norm(factor, 3*242)[-1244:]
        factor = factor[15:] - factor[:-15]
        factor = bk.move_max(factor, 19, 9, axis = 0)[-1210:]
        factor = get_norm(factor)
        return factor
    