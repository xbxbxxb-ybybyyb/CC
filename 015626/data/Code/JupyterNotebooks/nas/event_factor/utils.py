import numpy as np
import pandas as pd
from numpy import abs
from numpy import log
from numpy import sign
from scipy.stats import rankdata
from multifactor.IO import IO
import time
import os
import statsmodels.api as sm

# cross-sectional rank
def rank(df):
    return df.rank(pct=True)

# value of x d days ago
def delay(df, d=1):
    return df.shift(d)

# time-serial correlation of x and y for the past d days
def correlation(x, y, d=10):
    return x.rolling(d).corr(y.rolling(d))

# time-serial covariance of x and y for the past d days
def covariance(x, y, d=10):
    return x.rolling(d).cov(y.rolling(d))

# rescaled x such that sum(abs(x)) = a (the default is a = 1)
def scale(df, a=1):
    return df.mul(a).div(np.abs(df).sum())

# today’s value of x minus the value of x d days ago
def delta(df, d=1):
    return df.diff(d)


def signedpower(x, a):
    return x ^ a

# weighted moving average over the past d days with linearly decaying
# weights d, d – 1, …, 1 (rescaled to sum up to 1)
def decay_linear(df, period=10):
    # Clean data
    if df.isnull().values.any():
        df.fillna(method='ffill', inplace=True)
        df.fillna(method='bfill', inplace=True)
        df.fillna(value=0, inplace=True)
    na_lwma = np.zeros_like(df)
    na_lwma[:period, :] = df.iloc[:period, :]
    na_series = df.as_matrix()

    divisor = period * (period + 1) / 2
    y = (np.arange(period) + 1) * 1.0 / divisor

    for row in range(period - 1, df.shape[0]):
        x = na_series[row - period + 1: row + 1, :]
        na_lwma[row, :] = (np.dot(x.T, y))
    data = pd.DataFrame(na_lwma, index=df.index, columns=df.columns)

    return data

# time-series min over the past d days
def ts_min(df, d=10):
    return df.rolling(d).min()

# time-series max over the past d days
def ts_max(df, d=10):
    return df.rolling(d).max()

# which day ts_max(x, d) occurred on
def ts_argmax(df, d=10):
    return df.rolling(d).apply(np.argmax) + 1

# which day ts_min(x, d) occurred on
def ts_argmin(df, d=10):
    return df.rolling(d).apply(np.argmin) + 1

# time-series rank in the past d days
def ts_rank(df, d=10):
    def rolling_rank(x):
        return rankdata(x)[-1]
    return df.rolling(d).apply(rolling_rank)

# time-series sum over the past d days
def ts_sum(df, d=10):
    return df.rolling(d).sum()

def SUM(A, n):
    return A.rolling(n).sum()


def sma(df, d):
    return df.rolling(d).mean()

def MEAN(A, n):
    return A.rolling(n).mean()

# time-series product over the past d days
def product(df, d=10):
    def rolling_prod(x):
        return np.prod(x)

    return df.rolling(d).apply(rolling_prod)

# moving time-series standard deviation over the past d days
def stddev(df, d=10):
    return df.rolling(d).std()

def MIN(A,B):
    # 返回A,B中对应位置最小值
    if isinstance(A,pd.DataFrame)&isinstance(B,pd.DataFrame):
        output = A.copy(deep = True)
        output[A>B] = B
    elif isinstance(A,pd.DataFrame)&isinstance(B,(int,float)):
        output = A.copy(deep = True)
        output[A>B] = B
    elif isinstance(A,(int,float))&isinstance(B,pd.DataFrame):
        output = B.copy(deep = True)
        output[B>A] = A
    else:
        output = A if A<B else B
    return output

def MAX(A,B):
    # 返回A,B中对应位置最大值
    if isinstance(A,pd.DataFrame)&isinstance(B,pd.DataFrame):
        output = A.copy(deep = True)
        output[A<B] = B
    elif isinstance(A,pd.DataFrame)&isinstance(B,(int,float)):
        output = A.copy(deep = True)
        output[A<B] = B
    elif isinstance(A,(int,float))&isinstance(B,pd.DataFrame):
        output = B.copy(deep = True)
        output[B<A] = A
    else:
        output = A if A>B else B
    return output

def SMA(A, n, m):
    return A.ewm(alpha= m / n).mean()

# 前 n 期样本A对B做回归所得回归系数
def regbeta(A, B, n):
    def rolling_ols(y):
        # 回归
        X = sm.add_constant(B)
        model = sm.OLS(y, X)
        results = model.fit()
        return results.params[1]
    return A.rolling(n).apply(rolling_ols)
    
# 前 n 期样本A对B做回归所得残差
def regresi(A, B, n):
    def rolling_ols(y):
        # 回归
        X = sm.add_constant(B)
        model = sm.OLS(y, X)
        results = model.fit()
        return results.params[0]
    return A.rolling(n).apply(rolling_ols)
    
def WMA(A, n):
    weights = np.arange(n-1,-1,-1)
    weights = 0.9 * weights
    sum_weights = np.sum(weights)
    return A.rolling(n).apply(lambda x: np.sum(weights * x) / sum_weights)

def sequence(n):
    return np.arange(1, n + 1)

def sumac(A, n):
    return A.rolling(n).cumsum()
                                                                                                            
def norm_winsor(factor_pd, bound=3, winsor=False):
    factor_pd = factor_pd.copy()
    factor_pd = median_filter(factor_pd, mad=bound, winsor=winsor, inplace=True)
    std_ts = factor_pd.std(axis=1, ddof=0)
    std_ts.loc[std_ts == 0] = 1
    factor_pd = factor_pd.subtract(factor_pd.mean(axis=1), axis=0).divide(std_ts, axis=0)
    return factor_pd


def median_filter(factor_pd, mad=3, winsor=False, inplace=False):
    if not inplace:
        factor_pd = factor_pd.copy()
    dm = factor_pd.median(axis=1)
    # caution of symmetric uppper & lower bounds
    dist_dm = (factor_pd.subtract(dm, axis=0)).abs().median(axis=1)
    date_num, stock_num = factor_pd.shape
    fac_ub = pd.DataFrame(np.tile(dm + mad * dist_dm, [stock_num, 1]).T, index=factor_pd.index,
                          columns=factor_pd.columns)
    fac_lb = pd.DataFrame(np.tile(dm - mad * dist_dm, [stock_num, 1]).T, index=factor_pd.index,
                          columns=factor_pd.columns)
    if winsor:
        factor_pd[factor_pd > fac_ub] = np.nan
        factor_pd[factor_pd < fac_lb] = np.nan
    else:
        factor_pd[factor_pd > fac_ub] = fac_ub
        factor_pd[factor_pd < fac_lb] = fac_lb
    return factor_pd