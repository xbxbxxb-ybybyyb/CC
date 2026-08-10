from factor_generator import FactorGenerator
import pandas as pd
import numpy as np
import bottleneck as bk
from scipy.stats import rankdata

def rolling_norm(sig, window=1200, method='max_min'):
    assert isinstance(sig, pd.Series) or isinstance(sig, pd.DataFrame), 'the data structure of input is illegal, must be series or dataframe'
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
            return 2 * signal - 1    
        elif method == 'ts_rank':
            if isinstance(sig, pd.DataFrame):
                signal = pd.DataFrame(bk.move_rank(sig, window=window, min_count=int(window / 2), axis=0),
                                      index=sig.index, columns=sig.columns)
            elif isinstance(sig, pd.Series):
                signal = pd.Series(bk.move_rank(sig, window=window, min_count=int(window / 2), axis=0),
                                   index=sig.index, name=sig.name)
            return signal

def mean(A,d):
    output = A.rolling(d,min_periods=int(round(d/2))).mean()
    output.iloc[:d-1] = np.nan
    return output

def ts_rank_positive(df1, d):
    # moving time-series rank for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                           index=df1.index, name=df1.name)
    return (output+1)/2

def delay(A,n):
    return A.shift(periods=n)

class ts29_futures_zf(FactorGenerator):
    def __init__(self):
        required_columns = ['close','volume', 'recent_month_mask']
        super(ts29_futures_zf, self).__init__(required_columns=required_columns)

    def on_bar(self, data):
        mask = data['recent_month_mask']
        N = 10
        n2 = 20
        n3 = 200
        factor = -1 * (data['close'] - delay(data['close'], N)) / delay(data['close'],N) * data['volume']
        factor = ts_rank_positive(factor, n2)
        factor = mean(factor, n3)
        factor = rolling_norm(factor,242*5)
        factor = factor[mask].sum(axis=1)
        factor.name = self.__class__.__name__
        return pd.DataFrame(factor)