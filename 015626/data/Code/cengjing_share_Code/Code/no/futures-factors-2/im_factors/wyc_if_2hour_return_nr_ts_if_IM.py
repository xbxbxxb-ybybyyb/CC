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

class wyc_if_2hour_return_nr_ts_if_IM(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['close','turnover_rate','adjfactor']
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, df):
        cif = df['close_preadj'].values[-1531:]
        cif[abs(cif) < 1e-8] = np.nan
        ifreturn = cif[1:] / cif[:-1] - 1
        factor = bk.move_mean(ifreturn, 200, min_count=100, axis = 0)[-1330:]

        factor = rolling_norm(factor, 5 * 242)[-120:]

        t = df['turnover_rate'][-120:].values
        factor = factor * t
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 100, 50, axis = 0)[-20:]
        factor = np.nanmean(factor)
        return factor