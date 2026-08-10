# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import bottleneck as bk
from scipy.stats import rankdata
from joblib import Parallel, delayed

def ts_argmax(data, d):
    # which moment ts_max(x, d) occurred on.
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data, pd.DataFrame):
        output = pd.DataFrame(bk.move_argmax(data, window=d, min_count=int(d / 2), axis=0),
                              index=data.index, columns=data.columns)
    elif isinstance(data, pd.Series):
        output = pd.Series(bk.move_argmax(data, window=d, min_count=int(d / 2), axis=0),
                           index=data.index, name=data.name)
    elif isinstance(data, np.ndarray):
        output = bk.move_argmax(data, window=d, min_count=int(d / 2), axis=0)
    return (d - 1) - output


def ts_argmin(data, d):
    # which moment ts_min(x, d) occurred on.
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data, pd.DataFrame):
        output = pd.DataFrame(bk.move_argmin(data, window=d, min_count=int(d / 2), axis=0),
                              index=data.index, columns=data.columns)
    elif isinstance(data, pd.Series):
        output = pd.Series(bk.move_argmin(data, window=d, min_count=int(d / 2), axis=0),
                           index=data.index, name=data.name)
    elif isinstance(data, np.ndarray):
        output = bk.move_argmin(data, window=d, min_count=int(d / 2), axis=0)
    return (d - 1) - output

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
            
def rolling_normalize(df,x):
    def normalize(dd):
        a = (dd[-1] - dd.min()) / (dd.max() - dd.min())
        b = (a-0.5)*2
        return b
    return df.rolling(x, min_periods=int(x/2)).apply(normalize)

def ts_median(A, d):
    # moving time-series median for the past d periods
    if isinstance(A, pd.Series):
        A = A.to_frame()
    output = pd.DataFrame(bk.move_median(A, window=d, min_count=d//2, axis=0),
                          index=A.index, columns=A.columns)
    return output

def ts_mean(A, d):
    # moving time-series average for the past d periods
    if isinstance(A, pd.Series):
        A = A.to_frame()
    output = pd.DataFrame(bk.move_mean(A, window=d, min_count=d//2, axis=0),
                          index=A.index, columns=A.columns)
    return output

def ts_std(A, d):
    # moving time-series standard deviation over the past d periods
    if isinstance(A, pd.Series):
        A = A.to_frame()
    output = pd.DataFrame(bk.move_std(A, window=d, min_count=d//2, axis=0, ddof=1),
                          index=A.index, columns=A.columns)
    return output

def ts_skew(A, d):
    if isinstance(A, pd.Series):
        A = A.to_frame()
    # moving time-series skew over the past d periods
    output = A.rolling(d, min_periods=d//2).skew()
    output.iloc[:d - 1] = np.nan
    return output

def ts_kurt(A, d):
    if isinstance(A, pd.Series):
        A = A.to_frame()
    # moving time-series kurt over the past d periods
    output = A.rolling(d, min_periods=d//2).kurt()
    output.iloc[:d - 1] = np.nan
    return output

def delay(A,n):
    #A_(i-n)
    #A为df类型
    return A.shift(periods=n)

def correlation(A,B,d):
    #A,B过去d条数据的时序相关系数
    #A,B为df类型
    output = A.rolling(d, min_periods=int(round(d / 2))).corr(B.sort_index())
    output.iloc[:d-1] = np.nan
    return output

def delta(A,d):
    # A(t)-A(t-d),A为df类型
    return A-A.shift(d)

def SignedPower(A,a):
    # A^a,A为df类型
    return A**a

def decay_linear(A,d):
    # weighted moving average over the past d days with linearly decaying weights d, d – 1, …, 1 (rescaled to sum up to 1)
    # A为df类型
    output = pd.DataFrame(np.nan,index=A.index,columns=A.columns)
    wgts = np.arange(d)+1
    for i in range(len(output)-d+1):
        j = i+d
        output.iloc[j-1] = np.where(A.iloc[i:j].count()>round(d/2),np.average(A.iloc[i:j],weights=wgts,axis=0),np.nan)
    output.iloc[:d-1] = np.nan
    return output

def ts_min(A,d):
    # time-series min over the past d days. A is a dataframe.
    output = A.rolling(d,min_periods=int(round(d/2))).min()
    output.iloc[:d-1] = np.nan
    return output

def ts_max(A,d):
    # time-series max over the past d days. A is a dataframe.
    output = A.rolling(d,min_periods=int(round(d/2))).max()
    output.iloc[:d-1] = np.nan
    return output


def ts_argmax(A,d):
# which day ts_max(x, d) occurred on.
    data = A.copy()
    data.index = data.index.strftime('%Y%m%d%H%M').astype(float)
    output = pd.DataFrame(np.nan,index=data.index,columns=data.columns)
    for i in range(len(data)-d+1):
        j = i+d
        output.iloc[j-1] = np.where(data.iloc[i:j].count()>round(d/2),data.iloc[i:j].idxmax(),np.nan)
    output.index = pd.to_datetime(pd.Series(output.index).apply(round),format='%Y%m%d%H%M')
    output.index.name = 'dt'
    output.iloc[:d-1] = np.nan
    return output

def ts_argmin(A,d):
# which day ts_min(x, d) occurred on.
    data = A.copy()
    data.index = data.index.strftime('%Y%m%d%H%M').astype(float)
    output = pd.DataFrame(np.nan,index=data.index,columns=data.columns)
    for i in range(len(data)-d+1):
        j = i+d
        output.iloc[j-1] = np.where(data.iloc[i:j].count()>round(d/2),data.iloc[i:j].idxmin(),np.nan)
    output.index = pd.to_datetime(pd.Series(output.index).apply(round),format='%Y%m%d%H%M')
    output.index.name = 'dt'
    output.iloc[:d-1] = np.nan
    return output


def ts_rank_bk(A, d):
    # 时序rolling秩
    if isinstance(A, pd.Series):
        A = A.to_frame()
    output = pd.DataFrame(bk.move_rank(A, window=d, min_count=d//2, axis=0),
                          index=A.index, columns=A.columns)
    return output
    
def ts_rank(df1, d = 1200):
    # moving time-series rank for the past d periods
    assert isinstance(df1, pd.Series) or isinstance(df1, pd.DataFrame), 'input is not a dataframe or series'
    if d == 1:
        output = df1
    else:
        if isinstance(df1, pd.DataFrame):
            output = pd.DataFrame(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                                  index=df1.index, columns=df1.columns)
        elif isinstance(df1, pd.Series):
            output = pd.Series(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                               index=df1.index, name=df1.name)
    return output
#def ts_rank(df1, d):
#    # moving time-series rank for the past d periods
#    if isinstance(df1, pd.DataFrame):
#        output = pd.DataFrame(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
#                              index=df1.index, columns=df1.columns)
#    elif isinstance(df1, pd.Series):
#        output = pd.Series(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
#                           index=df1.index, name=df1.name)
#    return output

def ts_rank_positive(df1, d):
    # moving time-series rank for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                           index=df1.index, name=df1.name)
    return (output+1)/2
#def ts_rank(df, d=10):
#    def rolling_rank(x):
#        return rankdata(x)[-1]
#    return (df.rolling(d,min_periods=min(d//2,10)).apply(rolling_rank) - 1) / (d - 1)

def MIN(A,B):
    # 返回A,B中对应位置最小值
    if isinstance(A,pd.Series):
        A = A.to_frame()
    if isinstance(B,pd.Series):
        B = B.to_frame()
    if isinstance(A,pd.DataFrame)&isinstance(B,pd.DataFrame):
        output = A.copy()
        output[A>B] = B
    elif isinstance(A,pd.DataFrame)&isinstance(B,(int,float)):
        output = A.copy()
        output[A>B] = B
    elif isinstance(A,(int,float))&isinstance(B,pd.DataFrame):
        output = B.copy()
        output[B>A] = A
    else:
        output = A if A<B else B
    return output

def MAX(A,B):
    # 返回A,B中对应位置最大值
    if isinstance(A,pd.Series):
        A = A.to_frame()
    if isinstance(B,pd.Series):
        B = B.to_frame()
    if isinstance(A,pd.DataFrame)&isinstance(B,pd.DataFrame):
        output = A.copy()
        output[A<B] = B
    elif isinstance(A,pd.DataFrame)&isinstance(B,(int,float)):
        output = A.copy()
        output[A<B] = B
    elif isinstance(A,(int,float))&isinstance(B,pd.DataFrame):
        output = B.copy()
        output[B<A] = A
    else:
        output = A if A>B else B
    return output

def ts_sum(A,d):
    # time-series sum over the past d days
    output = A.rolling(d,min_periods=int(round(d/2))).sum()
    output.iloc[:d-1] = np.nan
    return output

def product(A,d):
    # time-series product over the past d days
    output = A.rolling(d,min_periods=round(d/2)).apply(lambda x:x.prod(),raw=False)
    output.iloc[:d-1] = np.nan
    return output

def std(A,d):
    # moving time-series standard deviation over the past d days
    # the same as stddev, for gtjas
    output = A.rolling(d,min_periods=int(round(d/2))).std()
    output.iloc[:d-1] = np.nan
    return output

def mean(A,d):
    # average for the past d days
    # the ame as rm, for gtjas
    output = A.rolling(d,min_periods=int(round(d/2))).mean()
    output.iloc[:d-1] = np.nan
    return output

def sign(A):
    output = np.sign(A.replace(np.nan,0))[~A.isnull()]
    return output

def log(A):
    output = np.log(A)
    return output

def count(A,d):
    # 过去d期满足条件的样本个数
    # A为取值是True or False的dataframe
    output = A.rolling(d).sum()
    return output

def regbeta(A,B,d):
    # 过去d期A对B回归的回归系数
    output = pd.DataFrame(np.nan,index=A.index,columns=A.columns)
    if isinstance(B,pd.DataFrame):
        for i in range(len(output)-d+1):
            j = i+d
            tA = A.iloc[i:j]
            tB = B.iloc[i:j]
            beta = ((tA-tA.mean())*(tB-tB.mean())).sum()/((tA-tA.mean())**2).sum()
            output.iloc[j-1] = np.where((tA.count()>round(d/2))&(tB.count()>round(d/2)),beta,np.nan)
    else: #A和1:d滚动回归
        tB = pd.DataFrame(np.tile(np.arange(d) + 1, (A.shape[1], 1)).T,columns=A.columns)
        for i in range(len(output)-d+1):
            j = i+d
            tA = A.iloc[i:j]
            tB.index = tA.index
            # beta = np.nansum((tA-np.nanmean(tA,axis=0))*(tB-np.nanmean(tB,axis=0)),axis=0)/np.nansum((tA-np.nanmean(tA,axis=0))**2,axis=0)
            beta = ((tA - tA.mean()) * (tB - tB.mean())).sum() / ((tA - tA.mean()) ** 2).sum()
            output.iloc[j-1] = np.where(tA.count()>round(d/2),beta,np.nan)
    # output.iloc[:d - 1] = np.nan
    return output

def sma(A,n,m):
    #移动平均 Y_i = m/n*A_i + (1-m/n)*Y_(i-1)
    output = A.ewm(alpha=m/n,adjust=False).mean()
    return output

def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.array(np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides))
    return rolling_table
    
def ts_truncated_ema(df1, d, alpha):
    # truncated ema
    if isinstance(df1, pd.DataFrame):
        assert df1.shape[1] == 1
        df1 = df1[df1.columns[0]]
            
    assert isinstance(df1, pd.Series), 'the data structure of input is illegal, must be series'
    assert 0 < alpha <1
    df1_copy = df1.copy()
    weight = np.append(alpha * np.array([(1 - alpha) ** i for i in range(d - 1)]), (1 - alpha) ** (d - 1))[::-1]
    output = pd.Series(np.nan, index=df1_copy.index, name=df1_copy.name)
    temp_y = rolling_window(df1_copy, d)
    temp_x = np.tile(weight, (temp_y.shape[0], 1))
    flag = np.isnan(temp_x) | np.isnan(temp_y)
    flag1 = np.sum(np.isnan(flag), axis=1)  # 缺失值个数
    flag1 = np.where(flag1 <= int(d / 2), 1, np.nan)
    temp_x[flag] = np.nan
    temp_y[flag] = np.nan
    output.iloc[d - 1:] = (np.nansum(temp_y * temp_x, axis=1) / np.nansum(temp_x, axis=1)) * flag1
    return output

def multi_processing_joblib(df, func, n_jobs=12, **kwargs):
    """
    cross-section multi-process for the dataframe
    :param df: dataframe
        the raw data
    :param func:
        the function acting on dataframe
    :param n_jobs: int
        the number of cores used, if n_jobs=-1, all cores will be used
    :param kwargs:
        the parameters in the param func.
    :return: dataframe
        the data after the use of function
    """
    assert isinstance(df, pd.DataFrame), 'the data structure of input is illegal, must be dataframe'
    results = Parallel(n_jobs=n_jobs)(delayed(func)(df[i], **kwargs) for i in df.columns)
    results_df = pd.DataFrame(results, index=df.columns, columns=df.index)
    return results_df.T
    
def sumif(A,d,condition):
    #对A过去d期满足条件的元素求和
    #A和condition均为dataframe
    tmp = A[condition]
    output = tmp.rolling(d,min_periods=int(round(d/2))).sum()
    output.iloc[:d - 1] = np.nan
    return output

def wma(A,d):
    # weighted moving average over the past d days with linearly decaying weights 1, 0.9, …, 0.9^(d-1) (rescaled to sum up to 1)
    # A为df类型
    output = pd.DataFrame(np.nan, index=A.index, columns=A.columns)
    wgts = [0.9**i for i in range(d-1,-1,-1)]
    for i in range(len(output) - d + 1):
        j = i + d
        output.iloc[j - 1] = np.where(A.iloc[i:j].count() > round(d / 2), np.average(A.iloc[i:j], weights=wgts, axis=0), np.nan)
    output.iloc[:d - 1] = np.nan
    return output

def filter(A,condition):
    #对A筛选符合condition的样本
    return A[condition]

def highday(A,d):
    # 计算A前n期时序中最大值距离当前时点的间隔
    data = A.copy()
    data.index = np.arange(len(A))
    output = pd.DataFrame(np.nan,index=A.index,columns=A.columns)
    for i in range(len(data)-d+1):
        j = i+d
        output.iloc[j-1] = np.where(data.iloc[i:j].count()>round(d/2),(j-1)-data.iloc[i:j].idxmax(),np.nan)
    output.iloc[:d - 1] = np.nan
    return output

def lowday(A,d):
    # 计算A前n期时序中最小值距离当前时点的间隔
    data = A.copy()
    data.index = np.arange(len(A))
    output = pd.DataFrame(np.nan,index=A.index,columns=A.columns)
    for i in range(len(data)-d+1):
        j = i+d
        output.iloc[j-1] = np.where(data.iloc[i:j].count()>round(d/2),(j-1)-data.iloc[i:j].idxmin(),np.nan)
    output.iloc[:d - 1] = np.nan
    return output

def ts_macd(x, timeperiod):
    signal_period, short_period, long_period = timeperiod, int(timeperiod * 1.5), timeperiod * 3
    _short = mean(x, short_period)
    _long = mean(x, long_period)
    DIF = _short - _long
    DEA = mean(DIF, signal_period)
    MACD = 2 * (DIF - DEA)
    return MACD

def ts_position(x, t):
    def get_position(ylist):
        smin = min(ylist)
        smax = max(ylist)
        y = ylist[-1]
        return (y - smin) / (smax - smin)
    return x.rolling(t, min_periods = t // 2).apply(get_position)

def ts_levelchange(x, t):
    return x - x.shift(t) + x

def ts_gain(x, t):
    return x / x.shift(t) - 1