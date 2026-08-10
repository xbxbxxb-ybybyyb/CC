# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import sys
from scipy.stats import rankdata

def delay(A,n):
    #A_(i-n)
    #A为df类型
    return A.shift(periods=n)

#def rank(A):
    #截面秩
    #A为df类型
    #return A.rank(axis=1,pct=True)

def correlation(A,B,d):
    #A,B过去d条数据的时序相关系数
    #A,B为df类型
    output = A.rolling(d, min_periods=int(round(d / 2))).corr(B.sort_index())
    output.iloc[:d-1] = np.nan
    return output

def corr(A,B,d):
    #A,B过去d条数据的时序相关系数
    #A,B为df类型
    #和correlation结果相同, gtjas
    output = A.rolling(d, min_periods=int(round(d / 2))).corr(B.sort_index())
    output.iloc[:d-1] = np.nan
    return output


def covariance(A,B,d):
    #A,B过去d条数据的时序协方差
    #A,B为df类型
    output = A.rolling(d, min_periods=int(round(d / 2))).cov(B.sort_index())
    output.iloc[:d-1] = np.nan
    return output

def coviance(A,B,d):
    #A,B过去d条数据的时序协方差
    #A,B为df类型
    #和covariance结果相同，gtjas
    output = A.rolling(d, min_periods=int(round(d / 2))).cov(B.sort_index())
    output.iloc[:d-1] = np.nan
    return output

def scale(A,a=1):
    # rescaled A such tha sum(abs(A))=a
    pass

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

def decaylinear(A,d):
    # weighted moving average over the past d days with linearly decaying weights d, d – 1, …, 1 (rescaled to sum up to 1)
    # A为df类型
    # 和decay_linear结果相同，gtjas
    output = pd.DataFrame(np.nan,index=A.index,columns=A.columns)
    wgts = np.arange(d)+1
    for i in range(len(output)-d+1):
        j = i+d
        output.iloc[j-1] = np.where(A.iloc[i:j].count()>round(d/2),np.average(A.iloc[i:j],weights=wgts,axis=0),np.nan)
    output.iloc[:d - 1] = np.nan
    return output

def indneutralize(A,g):
    # x cross-sectionally neutralized against groups g (subindustries, industries, sectors, etc.), i.e., x is cross-sectionally demeaned within each group g
    pass

def ts_O(A,d,func):
    # operator O applied across the time-series for the past d days; non-integer number of days d is converted to floor(d)
    pass

def ts_min(A,d):
    # time-series min over the past d days. A is a dataframe.
    output = A.rolling(d,min_periods=int(round(d/2))).min()
    output.iloc[:d-1] = np.nan
    return output

def tsmin(A,d):
    # time-series min over the past d days. A is a dataframe.
    # the same as ts_min, for gtjas
    output = A.rolling(d,min_periods=int(round(d/2))).min()
    output.iloc[:d-1] = np.nan
    return output

def ts_max(A,d):
    # time-series max over the past d days. A is a dataframe.
    output = A.rolling(d,min_periods=int(round(d/2))).max()
    output.iloc[:d-1] = np.nan
    return output

def tsmax(A,d):
    # time-series max over the past d days. A is a dataframe.
    # the same as ts_max, for gtjas
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



def ts_rank(df, d=10):
    def rolling_rank(x):
        return rankdata(x)[-1]
    return df.rolling(d,min_periods=min(d//2,10)).apply(rolling_rank)

def tsrank(A,d):
# time-series rank in the past d days
# the same as Ts_Rank for gtjas
    output = pd.DataFrame(np.nan,index=A.index,columns=A.columns)
    for i in range(len(output)-d+1):
        j = i+d
        output.iloc[j-1] = np.where(A.iloc[i:j].count()>round(d/2),A.iloc[i:j].rank().iloc[-1],np.nan)
    output.iloc[:d - 1] = np.nan
    return output

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

def prod(A,d):
    # time-series product over the past d days
    # the same as product,for gtjas
    output = A.rolling(d,min_periods=round(d/2)).apply(lambda x:x.prod(),raw=False)
    output.iloc[:d-1] = np.nan
    return output


def stddev(A,d):
    # moving time-series standard deviation over the past d days
    output = A.rolling(d,min_periods=int(round(d/2))).std()
    output.iloc[:d-1] = np.nan
    return output

def std(A,d):
    # moving time-series standard deviation over the past d days
    # the same as stddev, for gtjas
    output = A.rolling(d,min_periods=int(round(d/2))).std()
    output.iloc[:d-1] = np.nan
    return output

def rm(A,d):
    # average for the past d days
    output = A.rolling(d,min_periods=int(round(d/2))).mean()
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
    output = np.log(A[A>0])
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

def view_bar(num,tot,s):
    #查看计算进度
    rate = num/(tot-1)
    rate_num = (int(rate*100))
    n = rate_num//3
    r = '\r[%s>%s]%d%%-%s' % ('='*n,'-'*(33-n), rate_num, s)
    sys.stdout.write(r)
    sys.stdout.flush()
    if rate == 1:
        print('\n')

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

def norm_winsor(factor_pd, bound=3, winsor=False):
    factor_pd = factor_pd.copy()
    factor_pd = median_filter(factor_pd, mad=bound, winsor=winsor, inplace=True)
    std_ts = factor_pd.std(axis=1, ddof=0)
    std_ts.loc[std_ts == 0] = 1
    factor_pd = factor_pd.subtract(factor_pd.mean(axis=1), axis=0).divide(std_ts, axis=0)
    return factor_pd

