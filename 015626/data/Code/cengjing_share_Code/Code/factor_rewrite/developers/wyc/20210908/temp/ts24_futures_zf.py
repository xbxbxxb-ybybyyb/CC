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

def ts_max(A,d):
    output = A.rolling(d,min_periods=int(round(d/2))).max()
    output.iloc[:d-1] = np.nan
    return output
    
def ts_min(A,d):
    output = A.rolling(d,min_periods=int(round(d/2))).min()
    output.iloc[:d-1] = np.nan
    return output

class ts24_futures_zf(FactorGenerator):
    def __init__(self):
        required_columns = ['close','high','low', 'recent_month_mask']
        super(ts24_futures_zf, self).__init__(required_columns=required_columns)

    def on_bar(self, data):
        mask = data['recent_month_mask']
        N = 20
        wmadf = mean(data['close'], N)
        longc = ts_max(data['high'], N) - wmadf
        shortc = ts_min(data['low'], N) - wmadf
        factor =  (longc - shortc) / data['close']
        factor = ts_rank(factor, 80)
        factor = mean(factor, 40)
        factor = rolling_normalize(factor,242*5)
        # factor[factor<-0.8]=0
        factor = factor[mask].sum(axis=1)
        factor.name = self.__class__.__name__
        return pd.DataFrame(factor)