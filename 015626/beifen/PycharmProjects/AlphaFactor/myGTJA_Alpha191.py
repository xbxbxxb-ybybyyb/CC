import numpy as np
import pandas as pd
from numpy import abs
from numpy import log
from numpy import sign
from scipy.stats import rankdata
from multifactor.IO import IO
from multiprocessing import Pool
import statsmodels.api as sm
import time

def DELAY(A, n):
    return A.shift(n)

def MAX(A, B):
    if type(A) in [pd.DataFrame, pd.Series]:
        C = A.copy(deep = True)
        con = A > B
        C[~con] = B
        return C
    else:
        return max(A, B)

def MIN(A, B):
    if type(A) in [pd.DataFrame, pd.Series]:
        C = A.copy(deep=True)
        con = A < B
        C[~con] = B
        return C
    else:
        return min(A, B)

def ABS(A):
    return abs(A)

def RANK(A):
    return A.rank(pct = True)

def STD(A, n):
    return A.rolling(n).std()

def CORR(A, B, n):
    return A.rolling(n).corr(B.rolling(n))

def DELTA(A, n):
    return A - DELAY(A, n)

def LOG(A):
    return log(A)

def SUM(A, n):
    return A.rolling(n).sum()

def MEAN(A, n):
    return A.rolling(n).mean()

def TSRANK(A, n):
    def rolling_rank(x):
        return rankdata(x)[-1]
    return A.rolling(n).apply(rolling_rank)

def SIGN(A):
    return sign(A)

def COVIANCE(A, B, n):
    return A.rolling(n).cov(B.rolling(n))

def TSMIN(A, n):
    return A.rolling(n).min()

def TSMAX(A, n):
    return A.rolling(n).max()

def PROD(A, n):
    def rolling_prod(x):
        return np.prod(x)
    return A.rolling(n).apply(rolling_prod)

def REGBETA(A, B, n):
    def rolling_ols(y):
        # 回归
        X = sm.add_constant(B)
        model = sm.OLS(y, X)
        results = model.fit()
        return results.params[1]
    return A.rolling(n).apply(rolling_ols)

def SMA(A, n, m):
    return A.ewm(alpha= m / n).mean()

def WMA(A, n):
    weights = np.arange(n-1,-1,-1)
    weights = 0.9 * weights
    sum_weights = np.sum(weights)
    return A.rolling(n).apply(lambda x: np.sum(weights * x) / sum_weights)

def DECAYLINEAR(df, period):
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

def SEQUENCE(n):
    return np.arange(1, n + 1)

def SUMAC(A, n):
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

start_date = 20140101
end_date = 20180630
data = IO.read_data([start_date,end_date],columns = ['open','high','low','close','pct_chg','amt','volume','mkt_cap_ard'],alt = 'A:/zhangf/data/md/CHINA_STOCK/B8/WIND/MD_CHINA_STOCK_B8_filter.h5')
df = data.unstack()
OPEN = df['open']
HIGH = df['high']
LOW = df['low']
CLOSE = df['close']
VOLUME = df['volume'] * 100
RET = df['pct_chg']
VWAP = (df['amt'] * 1000) / (df['volume'] * 100 + 1)
AMOUNT = df['amt'] * 1000

# indexdf = IO.read_data([start_date,end_date], alt = 'Z:\warehouse\prod\MD\CHINA_INDEX\DAILY\WIND\MD_CHINA_INDEX_DAILY_WIND.h5')
# indexdf = indexdf[indexdf.index.get_level_values(1) == '000300.SH']
# BANCHMARKINDEXOPEN = indexdf['open']
# BANCHMARKINDEXCLOSE = indexdf['close']

DTM = OPEN.copy(deep = True)
con1 = OPEN <= DELAY(OPEN,1)
DTM[con1] = 0
DTM[~con1] = MAX((HIGH-OPEN),(OPEN-DELAY(OPEN,1)))

DBM = OPEN.copy(deep = True)
con1 = OPEN>=DELAY(OPEN,1)
DBM[con1] = 0
DBM[~con1] = MAX((OPEN-LOW),(OPEN-DELAY(OPEN,1)))
# DTM = 0 if OPEN<=DELAY(OPEN,1) else MAX((HIGH-OPEN),(OPEN-DELAY(OPEN,1)))
# DBM = 0 if OPEN>=DELAY(OPEN,1) else MAX((OPEN-LOW),(OPEN-DELAY(OPEN,1)))
TR = MAX(MAX(HIGH-LOW,ABS(HIGH-DELAY(CLOSE,1))),ABS(LOW-DELAY(CLOSE,1)))
HD = HIGH-DELAY(HIGH,1)
LD = DELAY(LOW,1)-LOW

def alpha1():
    return (-1 * CORR(RANK(DELTA(LOG(VOLUME), 1)), RANK(((CLOSE - OPEN) / OPEN)), 6))

def alpha2():
    return (-1 * DELTA((((CLOSE - LOW) - (HIGH - CLOSE)) / (HIGH - LOW)), 1))

def alpha3():
    temp = CLOSE.copy(deep = True)
    condtion1 = (CLOSE == DELAY(CLOSE, 1))
    condition2 = (CLOSE > DELAY(CLOSE, 1))
    temp[condtion1] = 0
    temp[~condtion1 & condition2] = CLOSE - MIN(LOW,DELAY(CLOSE,1))
    temp[~condtion1 & ~condition2] = CLOSE - MAX(HIGH,DELAY(CLOSE,1))
    return SUM(temp,6)

def alpha4():
    temp = CLOSE.copy(deep = True)
    con1 = (((SUM(CLOSE, 8) / 8) + STD(CLOSE, 8)) < (SUM(CLOSE, 2) / 2))
    con2 = ((SUM(CLOSE, 2) / 2) <((SUM(CLOSE, 8) / 8)- STD(CLOSE, 8)))
    con3 = ((1 < (VOLUME / MEAN(VOLUME, 20))) | ((VOLUME /MEAN(VOLUME, 20)) == 1))
    temp[con1] = -1
    temp[~con1 & con2] = 1
    temp[~con1 & ~con2 & con3] = 1
    temp[~con1 & ~con2 & con3] = -1
    return temp

def alpha5():
    return (-1 * TSMAX(CORR(TSRANK(VOLUME, 5), TSRANK(HIGH, 5), 5), 3))

def alpha6():
    return (RANK(SIGN(DELTA((((OPEN * 0.85) + (HIGH * 0.15))), 4)))*1)

def alpha7():
    return ((RANK(MAX((VWAP-CLOSE), 3)) + RANK(MIN((VWAP-CLOSE), 3))) * RANK(DELTA(VOLUME, 3)))

def alpha8():
    return RANK(DELTA(((((HIGH + LOW) / 2) * 0.2) + (VWAP * 0.8)), 4) * -1)

def alpha9():
    return SMA(((HIGH+LOW)/2-(DELAY(HIGH,1)+DELAY(LOW,1))/2)*(HIGH-LOW)/VOLUME,7,2)

def alpha10():
    temp = RET.copy(deep = True)
    temp[RET < 0] = STD(RET, 20)
    temp[RET >= 0] = CLOSE
    return RANK(MAX(temp ** 2, 5))

def alpha11():
    return SUM(((CLOSE-LOW)-(HIGH - CLOSE)) / (HIGH - LOW) * VOLUME, 6)

def alpha12():
    return (RANK((OPEN - (SUM(VWAP, 10) / 10)))) * (-1 * (RANK(ABS((CLOSE - VWAP)))))

def alpha13():
    return (((HIGH * LOW) ** 0.5) - VWAP)

def alpha14():
    return CLOSE - DELAY(CLOSE,5)

def alpha15():
    return OPEN/DELAY(CLOSE,1) - 1

def alpha16():
    return (-1 * TSMAX(RANK(CORR(RANK(VOLUME), RANK(VWAP), 5)), 5))

def alpha17():
    return RANK((VWAP - MAX(VWAP, 15))) * DELTA(CLOSE, 5)

def alpha18():
    return CLOSE / DELAY(CLOSE,5)

def alpha19():
    temp = CLOSE.copy(deep = True)
    con1 = CLOSE < DELAY(CLOSE, 5)
    temp[con1] = (CLOSE - DELAY(CLOSE, 5)) / DELAY(CLOSE, 5)
    con2 = CLOSE==DELAY(CLOSE, 5)
    temp[~con1 & con2] = 0
    temp[~con1 & ~con2] = (CLOSE - DELAY(CLOSE, 5)) / CLOSE
    return temp

def alpha20():
    return (CLOSE- DELAY(CLOSE,6))/DELAY(CLOSE,6)*100

def alpha21():
    return REGBETA(MEAN(CLOSE,6),SEQUENCE(6),6)

def alpha22():
    return SMA(((CLOSE-MEAN(CLOSE,6))/MEAN(CLOSE,6) - DELAY((CLOSE - MEAN(CLOSE,6))/MEAN(CLOSE,6),3)),12,1)

def alpha23():
    temp = CLOSE.copy(deep = True)
    temp[CLOSE > DELAY(CLOSE, 1)] = STD(CLOSE,20)
    temp[CLOSE <= DELAY(CLOSE, 1)] = 0
    a = SMA(temp, 20, 1)
    temp[CLOSE > DELAY(CLOSE, 1)] = 0
    temp[CLOSE <= DELAY(CLOSE, 1)] = STD(CLOSE, 20)
    b = SMA(temp, 20, 1)
    return a / (a + b) * 100

def alpha24():
    return SMA(CLOSE - DELAY(CLOSE,5), 5,1)

def alpha25():
    return ((-1 * RANK((DELTA(CLOSE, 7) * (1 - RANK(DECAYLINEAR((VOLUME / MEAN(VOLUME,20)), 9)))))) * (1 +RANK(SUM(RET, 250))))

def alpha26():
    return ((((SUM(CLOSE, 7) / 7) - CLOSE)) + ((CORR(VWAP, DELAY(CLOSE, 5), 230))))

def alpha27():
    return WMA((CLOSE - DELAY(CLOSE,3))/DELAY( CLOSE,3)*100+(CLOSE - DELAY(CLOSE,6))/DELAY(CLOSE,6)*100,12)

def alpha28():
    return 3*SMA((CLOSE - TSMIN(LOW,9))/(TSMAX(HIGH,9)-TSMIN(LOW,9))*100,3,1) - 2*SMA(SMA((CLOSE-TSMIN(LOW,9))/(MAX(HIGH,9) - TSMAX(LOW,9))*100,3,1),3,1)

def alpha29():
    return (CLOSE - DELAY(CLOSE,6))/DELAY(CLOSE,6) * VOLUME

# def alpha30():
# #     return WMA((REGRESI(CLOSE/DELAY(CLOSE)-1,MKT,SMB,HML,60))^2,20)

def alpha31():
    return (CLOSE - MEAN(CLOSE,12)) / MEAN(CLOSE,12) * 100

def alpha32():
    return (-1 * SUM(RANK(CORR(RANK(HIGH), RANK(VOLUME), 3)), 3))

def alpha33():
    return ((((-1 * TSMIN(LOW, 5)) + DELAY(TSMIN(LOW, 5), 5)) * RANK(((SUM(RET, 240) - SUM(RET, 20)) / 220))) * TSRANK(VOLUME, 5))

def alpha34():
    return MEAN(CLOSE,12)/CLOSE

def alpha35():
    return (MIN(RANK(DECAYLINEAR(DELTA(OPEN, 1), 15)), RANK(DECAYLINEAR(CORR((VOLUME), ((OPEN * 0.65) + (OPEN *0.35)), 17),7))) * 1)

def alpha36():
    return RANK(SUM(CORR(RANK(VOLUME), RANK(VWAP), 6), 2))

def alpha37():
    return (-1 * RANK(((SUM(OPEN, 5) * SUM(RET, 5)) - DELAY((SUM(OPEN, 5) * SUM(RET, 5)), 10))))

def alpha38():
    temp = HIGH.copy(deep = True)
    temp[((SUM(HIGH, 20) / 20) < HIGH)] = -1 * DELTA(HIGH, 2)
    temp[((SUM(HIGH, 20) / 20) >= HIGH)] = 0
    return temp

def alpha39():
    return ((RANK(DECAYLINEAR(DELTA((CLOSE), 2),8)) - RANK(DECAYLINEAR(CORR(((VWAP * 0.3) + (OPEN * 0.7)),SUM(MEAN( VOLUME ,180), 37), 14), 12))) * 1)

def alpha40():
    temp = VOLUME.copy(deep = True)
    temp[CLOSE<=DELAY(CLOSE,1)] = 0
    a = SUM(temp,26)
    temp = VOLUME.copy(deep=True)
    temp[CLOSE > DELAY(CLOSE, 1)] = 0
    b = SUM(temp,26)
    return a/b*100

def alpha41():
    return (RANK(MAX(DELTA((VWAP), 3), 5))*-1)

def alpha42():
    return ((-1 * RANK(STD(HIGH, 10))) * CORR(HIGH, VOLUME, 10))

def alpha43():
    temp = VOLUME.copy(deep = True)
    con1 = CLOSE>DELAY(CLOSE,1)
    con2 = CLOSE<DELAY(CLOSE,1)
    temp[~con1 & con2] = -1 * VOLUME
    temp[~con1 & ~con2] = 0
    return SUM(temp,6)

def alpha44():
    return (TSRANK(DECAYLINEAR(CORR(((LOW )), MEAN(VOLUME,10), 7), 6),4) + TSRANK(DECAYLINEAR(DELTA((VWAP),3), 10), 15))

def alpha45():
    return (RANK(DELTA((((CLOSE * 0.6) + (OPEN*0.4))), 1)) * RANK(CORR(VWAP, MEAN(VOLUME,150),15)))

def alpha46():
    return (MEAN(CLOSE,3)+MEAN(CLOSE,6)+MEAN(CLOSE,12)+MEAN(CLOSE,24))/(4* CLOSE)

def alpha47():
    return SMA((TSMAX(HIGH,6) - CLOSE)/(TSMAX(HIGH,6) - TSMIN(LOW,6))*100,9,1)

def alpha48():
    return (-1*((RANK(((SIGN((CLOSE - DELAY(CLOSE, 1))) + SIGN((DELAY(CLOSE, 1) - DELAY(CLOSE, 2)))) +SIGN((DELAY(CLOSE, 2) - DELAY(CLOSE, 3)))))) * SUM(VOLUME, 5)) / SUM(VOLUME, 20))

def alpha49():
    temp = CLOSE.copy(deep = True)
    con1 = (HIGH+LOW)>=(DELAY(HIGH,1)+DELAY(LOW,1))
    temp[con1] = 0
    temp[~con1] = MAX(ABS(HIGH-DELAY(HIGH,1)),ABS(LOW - DELAY(LOW,1)))
    a = SUM(temp, 12)
    temp = CLOSE.copy(deep=True)
    con2 = (HIGH + LOW) <= (DELAY(HIGH, 1) + DELAY(LOW, 1))
    temp[con2] = 0
    temp[~con2] = MAX(ABS(HIGH - DELAY(HIGH, 1)), ABS(LOW - DELAY(LOW, 1)))
    b = SUM(temp, 12)
    return a/ (a + b)

def alpha50():
    temp = CLOSE.copy(deep = True)
    con1 = (HIGH + LOW) <= (DELAY(HIGH, 1) + DELAY(LOW, 1))
    temp[con1] = 0
    temp[~con1] = MAX(ABS(HIGH-DELAY(HIGH, 1)), ABS(LOW-DELAY(LOW, 1)))
    a = SUM(temp, 12)

    con1 = (HIGH + LOW) >= (DELAY(HIGH, 1) + DELAY(LOW, 1))
    temp[con1] = 0
    temp[~con1] = MAX(ABS(HIGH - DELAY(HIGH, 1)), ABS(LOW - DELAY(LOW, 1)))
    b = SUM(temp, 12)

    return (a - b) / (a + b)

    # SUM((?0: ), 12)
    # / (SUM(((HIGH + LOW) <= (DELAY(HIGH, 1) + DELAY(LOW, 1))?0:MAX(ABS(HIGH- DELAY(HIGH, 1)), ABS(LOW- DELAY(LOW, 1)))), 12)
    # +SUM(((HIGH + LOW) >= (DELAY(HIGH, 1) + DELAY(LOW, 1))?0:MAX(ABS(HIGH -DELAY(HIGH, 1)), ABS(LOW-DELAY(LOW, 1)))), 12))
    # -SUM(((HIGH + LOW) >= (DELAY(HIGH, 1) + DELAY(LOW, 1))?0:MAX(ABS(HIGH -DELAY(HIGH, 1)), ABS(LOW-DELAY(LOW, 1)))), 12)
    # / (SUM(((HIGH + LOW) >= (DELAY(HIGH, 1) + DELAY(LOW, 1))?0:MAX(ABS(HIGH DELAY(HIGH, 1)), ABS(LOW DELAY(LOW, 1)))), 12)
    # +SUM(((HIGH + LOW) <= (DELAY(HIGH, 1) + DELAY(LOW, 1))?0: MAX(ABS(HIGH-DELAY(HIGH, 1)), ABS(LOW-DELAY(LOW, 1)))), 12))

def alpha51():
    temp = CLOSE.copy(deep=True)
    con1 = (HIGH + LOW) <= (DELAY(HIGH, 1) + DELAY(LOW, 1))
    temp[con1] = 0
    temp[~con1] = MAX(ABS(HIGH - DELAY(HIGH, 1)), ABS(LOW - DELAY(LOW, 1)))
    a = SUM(temp, 12)

    con1 = (HIGH + LOW) >= (DELAY(HIGH, 1) + DELAY(LOW, 1))
    temp[con1] = 0
    temp[~con1] = MAX(ABS(HIGH - DELAY(HIGH, 1)), ABS(LOW - DELAY(LOW, 1)))
    b = SUM(temp, 12)

    return a / (a + b)

def alpha52():
    return SUM(MAX(HIGH-DELAY((HIGH+LOW+CLOSE)/3,1),0),26)/SUM(MAX(DELAY((HIGH+LOW+CLOSE)/3,1) - LOW,0),26)*100

def alpha53():
    con1 = CLOSE>DELAY(CLOSE,1)
    return con1.rolling(12).sum() / 12 * 100

def alpha54():
    return (-1 * RANK((STD(ABS(CLOSE - OPEN),10) + (CLOSE - OPEN)) + CORR(CLOSE, OPEN,10)))

def alpha55():
    con1 = (ABS(HIGH - DELAY(CLOSE, 1)) > ABS(LOW-DELAY(CLOSE, 1))) & (ABS(HIGH - DELAY(CLOSE, 1)) > ABS(HIGH - DELAY(LOW, 1)))
    con2 = (ABS(LOW -DELAY(CLOSE, 1)) > ABS(HIGH - DELAY(LOW, 1)))  & (ABS(LOW - DELAY(CLOSE, 1)) > ABS(HIGH - DELAY(CLOSE, 1)))
    temp = CLOSE.copy(deep = True)
    temp[con1] = ABS(HIGH-DELAY(CLOSE, 1))+ABS(LOW-DELAY(CLOSE, 1)) / 2 + ABS(DELAY(CLOSE, 1)-DELAY(OPEN, 1)) / 4
    temp[~con1 & con2] =  ABS(LOW - DELAY(CLOSE, 1)) + ABS(HIGH-DELAY(CLOSE, 1)) / 2 + ABS(DELAY(CLOSE, 1) - DELAY(OPEN, 1)) / 4
    temp[~con1 & ~con2] = ABS(HIGH-DELAY(LOW, 1))+ABS(DELAY(CLOSE, 1)-DELAY(OPEN, 1)) / 4
    a = (CLOSE-DELAY(CLOSE, 1) + (CLOSE - OPEN) / 2 + DELAY(CLOSE, 1)-DELAY(OPEN, 1))
    return SUM(a / temp * MAX(ABS(HIGH-DELAY(CLOSE, 1)), ABS(LOW-DELAY(CLOSE, 1))), 20)
    # SUM(16 * (CLOSE-DELAY(CLOSE, 1) + (CLOSE OPEN) / 2 + DELAY(CLOSE, 1)-DELAY(OPEN, 1))
    # / ((ABS(HIGH - DELAY(CLOSE, 1)) > ABS(LOW-DELAY(CLOSE, 1))
    # & ABS(HIGH - DELAY(CLOSE, 1)) > ABS(HIGH - DELAY(LOW, 1))? ABS(HIGH-DELAY(CLOSE, 1))+ABS(LOW-DELAY(CLOSE, 1)) / 2
    # + ABS(DELAY(CLOSE, 1)-DELAY(OPEN, 1)) / 4: (ABS(LOW -DELAY(CLOSE, 1)) > ABS(HIGH - DELAY(LOW, 1))
    # & ABS(LOW - DELAY(CLOSE, 1)) > ABS(HIGH - DELAY(CLOSE, 1))?ABS(LOW - DELAY(CLOSE, 1))
    # + ABS(HIGH-DELAY(CLOSE, 1)) / 2 + ABS(DELAY(CLOSE, 1) - DELAY(OPEN, 1)) / 4:
    # ABS(HIGH-DELAY(LOW, 1))+ABS(DELAY(CLOSE, 1)-DELAY(OPEN, 1)) / 4)))
    # *MAX(ABS(HIGH-DELAY(CLOSE, 1)), ABS(LOW-DELAY(CLOSE, 1))), 20)

def alpha56():
    temp = CLOSE.copy(deep = True)
    con1 = (RANK((OPEN - TSMIN(OPEN, 12))) < RANK((RANK(CORR(SUM(((HIGH + LOW) / 2), 19), SUM(MEAN(VOLUME, 40), 19), 13)) ** 5)))
    temp[con1] = 1
    temp[~con1] = 0
    return temp

def alpha57():
    return SMA((CLOSE - TSMIN(LOW,9))/(TSMAX(HIGH,9) - TSMIN(LOW,9))*100,3,1)

def alpha58():
    con1 = CLOSE > DELAY(CLOSE, 1)
    return con1.rolling(20).sum() / 20 * 100
    # COUNT(CLOSE > DELAY(CLOSE, 1), 20) / 20 * 100

def alpha59():
    temp = CLOSE.copy(deep = True)
    con1 = CLOSE==DELAY(CLOSE, 1)
    temp[con1] = 0
    con2 = CLOSE > DELAY(CLOSE, 1)
    temp[~con1 & con2] = CLOSE - MIN(LOW, DELAY(CLOSE, 1))
    temp[~con1 & ~con2] = CLOSE - MAX(HIGH, DELAY(CLOSE, 1))
    return SUM(temp, 20)

def alpha60():
    return SUM(((CLOSE-LOW)-(HIGH-CLOSE))/(HIGH-LOW)*VOLUME,20)

def alpha61():
    return (MAX(RANK(DECAYLINEAR(DELTA(VWAP, 1), 12)),RANK(DECAYLINEAR(RANK(CORR((LOW),MEAN(VOLUME,80), 8)), 17))) * 1)

def alpha62():
    return (-1 * CORR(HIGH, RANK(VOLUME), 5))

def alpha63():
    return SMA(MAX(CLOSE-DELAY(CLOSE,1),0),6,1)/SMA(ABS(CLOSE - DELAY(CLOSE,1)),6,1)*100

def alpha64():
    return (MAX(RANK(DECAYLINEAR(CORR(RANK(VWAP), RANK(VOLUME), 4), 4)),
         RANK(DECAYLINEAR(MAX(CORR(RANK(CLOSE), RANK(MEAN(VOLUME, 60)), 4), 13), 14))) * 1)

def alpha65():
    return MEAN(CLOSE,6)/CLOSE

def alpha66():
    return (CLOSE - MEAN(CLOSE,6))/MEAN(CLOSE,6)*100

def alpha67():
    return SMA(MAX(CLOSE-DELAY(CLOSE,1),0),24,1)/SMA(ABS(CLOSE - DELAY(CLOSE,1)),24,1)*100

def alpha68():
    return SMA(((HIGH+LOW)/2-(DELAY(HIGH,1)+DELAY(LOW,1))/2)*(HIGH - LOW)/VOLUME,15,2)

def alpha69():
    con1 = SUM(DTM, 20) > SUM(DBM, 20)
    temp = CLOSE.copy(deep=True)
    temp[con1] = (SUM(DTM,20)- SUM(DBM, 20)) / SUM(DTM, 20)
    con2 = SUM(DTM, 20)==SUM(DBM,20)
    temp[~con1 & con2] = 0
    temp[~con1 & ~con2] = (SUM(DTM,20) - SUM(DBM, 20)) / SUM(DBM, 20)
    return temp

def alpha70():
    return STD(AMOUNT,6)

def alpha71():
    return (CLOSE-MEAN(CLOSE,24))/MEAN(CLOSE,24)*100

def alpha72():
    return SMA((TSMAX(HIGH,6)- CLOSE)/(TSMAX(HIGH,6) - TSMIN(LOW,6))*100,15,1)

def alpha73():
    return ((TSRANK(DECAYLINEAR(DECAYLINEAR(CORR((CLOSE), VOLUME, 10), 16), 4), 5)-RANK(DECAYLINEAR(CORR(VWAP, MEAN(VOLUME,30), 4),3))) * 1)

def alpha74():
    return (RANK(CORR(SUM(((LOW * 0.35) + (VWAP * 0.65)), 20), SUM(MEAN(VOLUME,40), 20), 7)) +RANK( CORR(RANK(VWAP), RANK(VOLUME), 6)))

# def alpha75():
#     con1 = (CLOSE > OPEN) & (BANCHMARKINDEXCLOSE < BANCHMARKINDEXOPEN)
#     con2 = BANCHMARKINDEXCLOSE < BANCHMARKINDEXOPEN
#     return con1.rolling(50).sum() / con2.rolling(50).sum()

def alpha76():
    return STD(ABS((CLOSE/DELAY(CLOSE,1)-1))/VOLUME,20)/MEAN(ABS((CLOSE/DELAY(CLOSE,1) -1))/VOLUME,20)

def alpha77():
    return MIN(RANK(DECAYLINEAR(((((HIGH + LOW) / 2) + HIGH) - (VWAP + HIGH)), 20)),RANK(DECAYLINEAR(CORR(((HIGH + LOW) / 2), MEAN(VOLUME,40), 3), 6)))

def alpha78():
    return ((HIGH+LOW+CLOSE)/3-WMA((HIGH+LOW+CLOSE)/3,12))/(0.015*MEAN(ABS(CLOSE -MEAN((HIGH+LOW+CLOSE)/3,12)),12))

def alpha79():
    return SMA(MAX(CLOSE-DELAY(CLOSE,1),0),12,1)/SMA(ABS(CLOSE - DELAY(CLOSE,1)),12,1)*100

def alpha80():
    return (VOLUME-DELAY(VOLUME,5))/DELAY(VOLUME,5)*100

def alpha81():
    return SMA(VOLUME, 21, 2)

def alpha82():
    return SMA((TSMAX(HIGH,6)- CLOSE)/(TSMAX(HIGH,6)- TSMIN(LOW,6))*100,20,1)

def alpha83():
    return (-1 * RANK(COVIANCE(RANK(HIGH), RANK(VOLUME), 5)))

def alpha84():
    temp = VOLUME.copy(deep = True)
    con1 = CLOSE==DELAY(CLOSE,1)
    temp[con1] = 0
    return SUM(temp,20)

def alpha85():
    return (TSRANK((VOLUME / MEAN(VOLUME,20)), 20) * TSRANK((-1 * DELTA(CLOSE, 7)), 8))

def alpha86():
    con1 = (0.25 < (((DELAY(CLOSE, 20)-DELAY(CLOSE, 10)) / 10) - ((DELAY(CLOSE, 10) -CLOSE) / 10)))
    temp = CLOSE.copy(deep = True)
    temp[con1] = -1
    con2 = ((((DELAY(CLOSE, 20) -DELAY(CLOSE, 10)) / 10)-((DELAY(CLOSE, 10)- CLOSE) / 10)) < 0)
    temp[~con1 & con2] = 1
    temp[~con1 & ~con2] = (-1 *(CLOSE - DELAY(CLOSE, 1)))
    return temp

def alpha87():
    return ((RANK(DECAYLINEAR(DELTA(VWAP, 4), 7)) + TSRANK(DECAYLINEAR(((((LOW * 0.9) + (LOW * 0.1)) -VWAP) /(OPEN-((HIGH + LOW) / 2))), 11), 7)) * -1)

def alpha88():
    return (CLOSE-DELAY(CLOSE,20))/DELAY(CLOSE,20)*100

def alpha89():
    return 2*(SMA(CLOSE,13,2)-SMA(CLOSE,27,2)- SMA(SMA(CLOSE,13,2) -SMA(CLOSE,27,2),10,2))

def alpha90():
    return ( RANK(CORR(RANK(VWAP), RANK(VOLUME), 5)) * -1)

def alpha91():
    return ((RANK((CLOSE - MAX(CLOSE, 5)))*RANK(CORR((MEAN(VOLUME,40)), LOW, 5))) * -1)

def alpha92():
    return (MAX(RANK(DECAYLINEAR(DELTA(((CLOSE * 0.35) + (VWAP *0.65)), 2), 3)),TSRANK(DECAYLINEAR(ABS(CORR((MEAN(VOLUME,180)), CLOSE, 13)), 5), 15)) * -1)

def alpha93():
    con1 = OPEN>=DELAY(OPEN,1)
    temp = CLOSE.copy(deep = True)
    temp[con1] = 0
    temp[~con1] = MAX((OPEN-LOW),(OPEN- DELAY(OPEN,1)))
    return SUM(temp,20)

def alpha94():
    temp = VOLUME.copy(deep = True)
    temp[CLOSE == DELAY(CLOSE, 1)] = 0
    return SUM(temp, 30)

def alpha95():
    return STD(AMOUNT,20)

def alpha96():
    return SMA(SMA((CLOSE-TSMIN(LOW,9))/( TSMAX(HIGH,9)- TSMIN(LOW, 9)) * 100, 3, 1),3,1)

def alpha97():
    return STD(VOLUME,10)

def alpha98():
    con1 = ((DELTA((SUM(CLOSE, 100) / 100), 100) / DELAY(CLOSE, 100)) <= 0.05)
    temp = CLOSE.copy(deep = True)
    temp[con1] = ( -1 * (CLOSE - TSMIN(CLOSE, 100)))
    temp[~con1] = -1 * DELTA(CLOSE, 3)
    return temp

def alpha99():
    return (-1 * RANK(COVIANCE(RANK(CLOSE), RANK(VOLUME), 5)))

def alpha100():
    return STD(VOLUME,20)


# wronglist = []
# for i in range(11,101):
#     if i in [31]:
#         continue
#     alpha_name = 'alpha' + str(i)
#     print(alpha_name)
#
#     try:
#         start_time = time.time()
#         data[alpha_name] = eval(alpha_name)().stack()
#         data[alpha_name] = norm_winsor(data[alpha_name].unstack()).stack()
#         print(alpha_name, time.time() - start_time)
#         IO.pd_hdf5_writer(data[alpha_name].to_frame(), 'A:\\weiyc\\factor\\factor191\\factor191\\' + alpha_name + '.h5', dataset=alpha_name)
#         data.drop([alpha_name], axis = 1, inplace=True)
#     except:
#         wronglist.append(alpha_name)
#
# print('wrong',wronglist)

def getfactor(alpha_name):
    start_time = time.time()
    data[alpha_name] = eval(alpha_name)().stack()
    data[alpha_name] = norm_winsor(data[alpha_name].unstack()).stack()
    print(alpha_name, time.time() - start_time)
    IO.pd_hdf5_writer(data[alpha_name].to_frame(), 'A:\\weiyc\\factor\\factor191\\factor191\\' + alpha_name + '.h5',
                      dataset=alpha_name)
    data.drop([alpha_name], axis=1, inplace=True)

alphalist = []
for i in range(1,101):
    if i in [30,75]:
        continue
    alpha_name = 'alpha' + str(i)
    alphalist.append(alpha_name)

for alpha_name in alphalist[:10]:
    getfactor(alpha_name)
