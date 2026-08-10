from factor_generator import FactorGenerator
import pandas as pd
import numpy as np
import bottleneck as bk
from scipy.stats import rankdata

def rolling_normalize(sig, window = 100):
    sig_max = sig.rolling(window,min_periods=int(window/2)).max()
    sig_min = sig.rolling(window,min_periods=int(window/2)).min()
    return ((sig-sig_min)/(sig_max-sig_min))*2-1

def mean(A,d):
    output = A.rolling(d,min_periods=int(round(d/2))).mean()
    output.iloc[:d-1] = np.nan
    return output

def ts_rank(df, d=10):
    def rolling_rank(x):
        return rankdata(x)[-1]
    return df.rolling(d,min_periods=min(d//2,10)).apply(rolling_rank,raw=True)

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
        factor = ts_rank(factor, n2)
        factor = mean(factor, n3)
        factor = rolling_normalize(factor,242*5)
        factor = factor[mask].sum(axis=1)
        factor.name = self.__class__.__name__
        return pd.DataFrame(factor)