from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

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

def get_delta(data, n):
    return data[n:] - data[:-n]

class wyc_ts5_future_nr_as(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 12
    data_dict = dict()
    data_dict['Stock'] = ['close','amount','adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True 

    def calculate(self, df):
        N = 45
        close = df['close_preadj'].values
        origin = get_delta((bk.move_sum(close, N,int(N/2), axis =0) / N), N) / close[:-N]
        change1 = -1 * (close - bk.move_min(close, N,int(N/2), axis =0))[N:]
        change2 = -1 * get_delta(close, 3)[N-3:]
        factor = np.where(origin<=0.05,change1,change2)[-1530 - 5*242:]

        factor = bk.move_rank(-1*factor, 1200, 600, axis = 0)[-5*242 - 330:]
        factor = bk.move_mean(factor,15,7,axis = 0)[-5*242 - 315:]

        factor = rolling_norm(factor, 5 * 242)[-315:]

        a = df['amount'].values[-315:]
        factor = factor * a
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 300, 150, axis = 0)[-15:]
        factor = np.nanmean(factor)
     
        return factor