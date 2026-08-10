import numpy as np
import pandas as pd
from numpy import abs
from numpy import log
from numpy import sqrt
from numpy import sign
from scipy.stats import rankdata
from multifactor.IO import IO
from multiprocessing import Pool,Manager
import statsmodels.api as sm
import time
import os
from utils import *


class gtja_Alphas(object):
    def __init__(self, df):
        self.open = (df['open'] * df['adjfactor']).unstack()
        self.high = (df['high'] * df['adjfactor']).unstack()
        self.low = (df['low'] * df['adjfactor']).unstack()
        self.close = (df['close'] * df['adjfactor']).unstack()
        self.volume = ((df['volume'] / df['adjfactor']) * 100).unstack()
        self.ret = df['pct_chg'].unstack()
        self.amount = (df['amt'] * 1000).unstack()
        self.vwap = (df['vwap'] * df['adjfactor']).unstack()

        self.dtm = self.open.copy(deep = True)
        con1 = self.open <= delay(self.open,1)
        self.dtm[con1] = 0
        self.dtm[~con1] = MAX((self.high-self.open),(self.open-delay(self.open,1)))

        self.dbm = self.open.copy(deep = True)
        con1 = self.open>=delay(self.open,1)
        self.dbm[con1] = 0
        self.dbm[~con1] = MAX((self.open-self.low),(self.open-delay(self.open,1)))

        self.tr = MAX(MAX(self.high-self.low,abs(self.high-delay(self.close,1))),abs(self.low-delay(self.close,1)))
        self.hd = self.high-delay(self.high,1)
        self.ld = delay(self.low,1)-self.low

        self.temp = df['pct_chg'].unstack()

    # ACD指标将市场分为两股收集（买入）及派发（估出）的力量。
    # 若当天收市价高于昨天收市价，则收集力量等于当天收市价与真实低位之差。
    # 真实低位是当天低位与昨天收市价两者中的最低者。
    # 若当天收市价低于昨天收市价，则派发力量等于当天当天收市价与真实高位之
    # 差。真实高位是当天高位与昨天收市价两者较高者；
    # 若将收集力量（正数）及派发力量（负数）相加，我们便可得到市场的净收集
    # 力量，从而了解市场的强弱。
    def gfalpha1(self):
        LC=delay(self.close,1)
        temp = self.temp
        temp[self.close>LC] = self.close-MIN(self.low,LC)
        temp[self.close<LC] = self.close-MAX(self.high,LC)
        temp[self.close==LC] = 0
        ACD=SUM(temp,6)
        return -1 * ACD
        
    def gfalpha2(self):
        LC=delay(self.close,1)
        temp = self.temp
        temp[self.close>LC] = self.close-MIN(self.low,LC)
        temp[self.close<LC] = self.close-MAX(self.high,LC)
        temp[self.close==LC] = 0
        ACD=SUM(temp,20)
        return -1 * ACD

    # AD指标将每日的成交量通过价格加权累计，用以计算成交量的动量。
    def gfalpha6(self):
        return -1 * ((self.close-self.low)-(self.high-self.close))/(self.high-self.low)*self.volume
        
    def gfalpha7(self):
        return -1 * SUM(((self.close-self.low)-(self.high-self.close))/(self.high-self.low)*self.volume,6)
        
    def gfalpha8(self):
        return -1 * SUM(((self.close-self.low)-(self.high-self.close))/(self.high-self.low)*self.volume,20)

    # AR指标是反映市场当前情况下多空双方力量发展对比的结果。它是以当日的开
    # 盘价为基点。与当日最高价相比较，依固定公式计算出来的强弱指标。
    def gfalpha9(self):
        M = 4
        return -1 * SUM(self.high-self.open,M)/SUM(self.open-self.low,M)*100

    # BR指标也是反映当前情况下多空双方力量争斗的结果。不同的是它是以前一日
    # 的收盘价为基础，与当日的最高价、最低价相比较，依固定公式计算出来的强弱指标。
    def gfalpha10(self):
        M=4
        return -1 * SUM(MAX(0,self.high-delay(self.close,1)),M)/SUM(MAX(0,delay(self.close,1)-self.low),M)*100
        
    def gfalpha11(self):
        M=4
        return SUM(MAX(0,self.high-delay(self.close,1)),M)/SUM(MAX(0,delay(self.close,1)-self.low),M)*100 - SUM(self.high-self.open,M)/SUM(self.open-self.low,M)*100
    #ARC指标是股票的价格变化率RC指标的均值，用以判断前一段交易周期内股票的平均价格变化率。
    def gfalpha12(self):
        M = 4
        RC=self.close/delay(self.close,M)
        return -1 * SMA(delay(RC,1),M,1)
    # Aroon上升数=[(计算期天数-最高价后的天数)/计算期天数]*100
    def gfalpha13(self):
        M = 10
        up = ts_argmax(self.close, M) / M * 100
        return up
    #  Aroon下降数=[(计算期天数-最低价后的天数)/计算期天数]*100
    def gfalpha14(self):
        M = 10
        down = ts_argmin(self.close, M) / M * 100
        return -1 * down
        
    def gfalpha15(self):
        return self.gfalpha13 + self.gfalpha14()

    # 累计振动升降指标(ASI)，由威尔斯·王尔德（Welles Wilder）所创。ASI指标
    # 以开盘、最高、最低、收盘价与前一交易日的各种价格相比较作为计算因子，研判市场的方向性。
    def gfalpha16(self):
        LC=delay(self.close,1)
        AA=abs(self.high-LC)
        BB=abs(self.low-LC)
        CC=abs(self.high-delay(self.low,1))
        DD=abs(LC-delay(self.open,1))
        R = self.temp
        con1 = AA > BB & AA > CC
        R[con1] = AA + BB / 2 + DD / 4
        con2 = BB > CC & BB > AA
        R[~con1 & con2] = BB + AA / 2 + DD / 4
        R[~con1 & ~con2] = CC + DD / 4
        X = (self.close - LC + (self.close - self.open) / 2 + LC - delay(self.open, 1))
        SI = 16 * X / R * MAX(AA, BB)
        return -1 * SI
    
    def gfalpha17(self):
        LC = delay(self.close, 1)
        AA = abs(self.high - LC)
        BB = abs(self.low - LC)
        CC = abs(self.high - delay(self.low, 1))
        DD = abs(LC - delay(self.open, 1))
        R = self.temp
        con1 = AA > BB & AA > CC
        R[con1] = AA + BB / 2 + DD / 4
        con2 = BB > CC & BB > AA
        R[~con1 & con2] = BB + AA / 2 + DD / 4
        R[~con1 & ~con2] = CC + DD / 4
        X = (self.close - LC + (self.close - self.open) / 2 + LC - delay(self.open, 1))
        SI = 16 * X / R * MAX(AA, BB)
        return -1 * ts_sum(SI, 10)

    # ATR不指示价格的变动方向，只表示价格的波动程度。而价格波动幅度的突破通
    # 常也预示着价格的突破。即：该指标价值越高，趋势改变的可能性就越高；该指标
    # 的价值越低，趋势的移动性就越弱。

    def gfalpha18(self):
        m = 12
        TR1 = MAX(MAX((self.high - self.low), abs(delay(self.close, 1) - self.high)), abs(delay(self.close, 1) - self.low))
        ATR = -1 * MEAN(TR1, m)

    def gfalpha19(self):
        m = 6
        TR1 = MAX(MAX((self.high - self.low), abs(delay(self.close, 1) - self.high)), abs(delay(self.close, 1) - self.low))
        ATR = -1 * MEAN(TR1, m)

    # BBI多空指标，是一种将不同日数移动平均线加权平均之后的综合指标，在BBI指标中，近期数据
    # 较多，远期数据利用次数较少，因而是一种变相的加权计算。BBI指标既有短期移动
    # 平均线的灵敏，又有明显的中期趋势特征。

    def gfalpha20(self):
        M1 = 3
        M2 = 6
        M3 = 12
        M4 = 24
        BBI = (MEAN(self.close, M1) + MEAN(self.close, M2) + MEAN(self.close, M3) + MEAN(self.close, M4)) / 4
        return BBI / self.close

    def gfalpha21(self):
        M1 = 3
        M2 = 6
        M3 = 12
        M4 = 24
        BBI = (MEAN(self.close, M1) + MEAN(self.close, M2) + MEAN(self.close, M3) + MEAN(self.close, M4)) / 4
        return BBI

    # BIAS乖离率
    def gfalpha22(self):
        P1 = 4
        return (self.close - MEAN(self.close, P1)) / MEAN(self.close, P1) * 100

    def gfalpha23(self):
        P1 = 6
        return (self.close - MEAN(self.close, P1)) / MEAN(self.close, P1) * 100

    def gfalpha24(self):
        P1 = 12
        return (self.close - MEAN(self.close, P1)) / MEAN(self.close, P1) * 100

    # CCI 顺势行情
    def gfalpha25(self):
        M = 8
        TYP = (self.high + self.low + self.close) / 3
        CCI = (TYP - MEAN(TYP, M)) / (0.015 * ts_sum(MEAN(TYP, M) - self.close, M))
        return CCI

    def gfalpha26(self):
        AD = self.volume * [(self.close - self.low) - (self.high - self.close)] / (self.high - self.low)
        return -1 * WMA(AD, 10) - WMA(AD, 3)

    def gfalpha27(self):
        temp = WMA(delay(self.high, 10) - delay(self.low, 10), 10)
        return -1 * (WMA(self.high - self.low, 10) - temp) / temp * 100

    # Chande钱德动量摆动指标
    def gfalpha28(self):
        N = 4
        con1 = self.close - delay(self.close, 1) > 0
        CZ1 = self.temp
        CZ1[con1] = self.close - delay(self.close, 1)
        CZ1[~con1] = 0

        con2 = self.close - delay(self.close, 1) < 0
        CZ2 = self.temp
        CZ2[con2] = abs(self.close - delay(self.close, 1))
        CZ2[~con2] = 0

        SU = SUM(CZ1, N)
        SD = SUM(CZ2, N)
        return -1 * (SU - SD) / (SU + SD) * 100

    def gfalpha29(self):
        N = 4
        con1 = self.close - delay(self.close, 1) > 0
        CZ1 = self.temp
        CZ1[con1] = self.close - delay(self.close, 1)
        CZ1[~con1] = 0

        SU = SUM(CZ1, N)

        return -1 * SU

    def gfalpha30(self):
        N = 4
        con2 = self.close - delay(self.close, 1) < 0
        CZ2 = self.temp
        CZ2[con2] = abs(self.close - delay(self.close, 1))
        CZ2[~con2] = 0

        SD = SUM(CZ2, N)
        return -1 * SD

    def gfalpha31(self):
        N1 = 4
        N2 = 8
        N3 = 8
        Rn1 = (self.close - delay(self.close, N1)) / delay(self.close, N1) * 100
        Rn2 = (self.close - delay(self.close, N2)) / delay(self.close, N2) * 100
        RCn1n2 = Rn1 + Rn2

        return -1 * WMA(RCn1n2, N3)

    def gfalpha32(self):
        M = 6
        MID = (self.high + self.low + self.close) / 3
        return -1 * SUM(MAX(0, self.high - delay(MID, 1)), M) / SUM(MAX(0, delay(MID, 1) - self.low), M) * 100

    def gfalpha33(self):
        P = 6
        N = 6
        W = 4
        BIAS = (self.close - MEAN(self.close, P)) / MEAN(self.close, P)
        DIF = (BIAS - delay(BIAS, N))
        return -1 * SMA(DIF, W, 1)

    def gfalpha34(self):
        N = 8
        con1 = (self.high + self.low) <= delay(self.high, 1) + delay(self.low, 1)
        DMZ = self.temp
        DMZ[con1] = 0
        DMZ[~con1] = MAX(abs(self.high - delay(self.high, 1)), abs(self.low - delay(self.low,1)))

        con2 = (self.high + self.low) >= delay(self.high, 1) + delay(self.low, 1)
        DMF = self.temp
        DMF[con2] = 0
        DMF[~con2] = MAX(abs(self.high - delay(self.high, 1)), abs(self.low - delay(self.low,1)))

        DIZ = SUM(DMZ, N) / (SUM(DMZ, N) + SUM(DMF, N))
        DIF = SUM(DMF, N) / (SUM(DMF, N) + SUM(DMZ, N))
        return DIF - DIZ

    def gfalpha35(self):
        N = 8
        con1 = (self.high + self.low) <= delay(self.high, 1) + delay(self.low, 1)
        DMZ = self.temp
        DMZ[con1] = 0
        DMZ[~con1] = MAX(abs(self.high - delay(self.high, 1)), abs(self.low - delay(self.low, 1)))

        con2 = (self.high + self.low) >= delay(self.high, 1) + delay(self.low, 1)
        DMF = self.temp
        DMF[con2] = 0
        DMF[~con2] = MAX(abs(self.high - delay(self.high, 1)), abs(self.low - delay(self.low, 1)))

        DIZ = SUM(DMZ, N) / (SUM(DMZ, N) + SUM(DMF, N))
        # DIF = SUM(DMF, N) / (SUM(DMF, N) + SUM(DMZ, N))
        return -1 * DIZ

    def gfalpha36(self):
        N = 8
        con1 = (self.high + self.low) <= delay(self.high, 1) + delay(self.low, 1)
        DMZ = self.temp
        DMZ[con1] = 0
        DMZ[~con1] = MAX(abs(self.high - delay(self.high, 1)), abs(self.low - delay(self.low, 1)))

        con2 = (self.high + self.low) >= delay(self.high, 1) + delay(self.low, 1)
        DMF = self.temp
        DMF[con2] = 0
        DMF[~con2] = MAX(abs(self.high - delay(self.high, 1)), abs(self.low - delay(self.low, 1)))

        # DIZ = SUM(DMZ, N) / (SUM(DMZ, N) + SUM(DMF, N))
        DIF = SUM(DMF, N) / (SUM(DMF, N) + SUM(DMZ, N))
        return DIF

    def gfalpha37(self):
        P = 8
        M = 6
        TR1 = SUM(MAX(MAX(self.high - self.low, abs(self.high - delay(self.close, 1))), abs(self.low - delay(self.close, 1))), P)
        HD = self.high - delay(self.high, 1)
        LD = delay(self.low, 1) - self.low
        temp = self.temp
        con1 = HD > 0 & HD > LD
        temp[con1] = HD
        temp[~con1] = 0
        DMP = SUM(temp, P)
        PDI = DMP * 100 / TR1

        con2 = LD > 0 & LD > HD
        temp[con2] = LD
        temp[~con2] = 0
        DMM = SUM(temp, P)
        MDI = DMM * 100 / TR1

        ADX = MEAN(abs(MDI - PDI) / (MDI + PDI) * 100, M)
        return -1 * ADX

    def gfalpha38(self):
        P = 8
        M = 6
        TR1 = SUM(MAX(MAX(self.high - self.low, abs(self.high - delay(self.close, 1))), abs(self.low - delay(self.close, 1))), P)
        HD = self.high - delay(self.high, 1)
        LD = delay(self.low, 1) - self.low
        temp = self.temp
        con1 = HD > 0 & HD > LD
        temp[con1] = HD
        temp[~con1] = 0
        DMP = SUM(temp, P)
        PDI = DMP * 100 / TR1

        con2 = LD > 0 & LD > HD
        temp[con2] = LD
        temp[~con2] = 0
        DMM = SUM(temp, P)
        MDI = DMM * 100 / TR1

        ADX = MEAN(abs(MDI - PDI) / (MDI + PDI) * 100, M)
        return (ADX+delay(ADX,M))/2

    def gfalpha40(self):
        N = 6
        return WMA(((self.high+self.low)/2-(delay(self.high,1)+delay(self.low,1))/2)*(self.high-self.low)/self.volume, N)

    def gfalpha41(self):
        N = 14
        return WMA(((self.high + self.low) / 2 - (delay(self.high, 1) + delay(self.low, 1)) / 2) * (self.high - self.low) / self.volume, N)

    def gfalpha42(self):
        N = 8
        long = ts_max(self.high, N) - WMA(self.close, N)
        short = ts_min(self.low, N) - WMA(self.close, N)
        return -1 * (long - short) / self.close

    def gfalpha45(self):
        N = 8
        P1 = 6
        P2 = 6
        RSV = (self.close - ts_min(self.low, N)) / (ts_max(self.high, N) - ts_min(self.low, N)) * 100
        K = SMA(RSV, P1, 1)
        # D = SMA(K, P2, 1)
        # J = 3 * K - 2 * D
        return K

    def gfalpha46(self):
        N = 8
        P1 = 6
        P2 = 6
        RSV = (self.close - ts_min(self.low, N)) / (ts_max(self.high, N) - ts_min(self.low, N)) * 100
        K = SMA(RSV, P1, 1)
        D = SMA(K, P2, 1)
        # J = 3 * K - 2 * D
        return D

    def gfalpha46(self):
        N = 8
        P1 = 6
        P2 = 6
        RSV = (self.close - ts_min(self.low, N)) / (ts_max(self.high, N) - ts_min(self.low, N)) * 100
        K = SMA(RSV, P1, 1)
        D = SMA(K, P2, 1)
        J = 3 * K - 2 * D
        return J

    def gfalpha49(self):
        return MEAN(self.close, 8) / self.close

    def gfalpha52(self):
        S = 4
        P = 8
        M = 6
        DIFF = WMA(self.close, S) - WMA(self.close, P)
        DEA = WMA(DIFF, M)
        return -2 * (DIFF - DEA)

    def gfalpha53(self):
        return WMA(self.high-self.low,9)/WMA(WMA(self.high-self.low,9),9)

    def gfalpha54(self):
        N = 6
        TYP = (self.high + self.low + self.close) / 3
        a = self.temp
        a[TYP > delay(TYP, 1)] = TYP * self.volume
        a[TYP <= delay(TYP, 1)] = 0
        b = self.temp
        b[TYP < delay(TYP, 1)] = TYP * self.volume
        b[TYP >= delay(TYP, 1)] = 0
        V1 = SUM(a, N) / SUM(b, N)
        return 100 - (100 / (1 + V1))

    def gfalpha55(self):
        N = 6
        N1 = 4
        N2 = 8
        MTM = self.close - delay(self.close, 1);
        MTMMA = SMA(MTM, N, 1);
        DIF = MEAN(delay(MTMMA, 1), N1) - MEAN(delay(MTMMA, 1), N2)
        return SMA(DIF, 10, 1)

    def gfalpha56(self):
        N = 6
        Flow = (self.close + self.high + self.low) / 3 * self.volume
        return ts_sum(Flow, N)

    def gfslpha57(self):
        n = 6
        m = 4
        MTM = self.close - delay(self.close, n)
        return SMA(MTM, m, 1)

    def gfalpha59(self):
        con1 = self.close > delay(self.close, 1)
        OBV = self.temp
        OBV[con1] = self.volume
        con2 = self.close < delay(self.close, 1)
        OBV[~con1 & con2] = -1 * self.volume
        OBV[~con1 & ~con2] = 0
        return -1 * OBV

    def gfalpha60(self):
        con1 = self.close > delay(self.close, 1)
        OBV = self.temp
        OBV[con1] = self.volume
        con2 = self.close < delay(self.close, 1)
        OBV[~con1 & con2] = -1 * self.volume
        OBV[~con1 & ~con2] = 0
        return -1 * ts_sum(OBV, 6)

    def gfalpha61(self):
        con1 = self.close > delay(self.close, 1)
        OBV = self.temp
        OBV[con1] = self.volume
        con2 = self.close < delay(self.close, 1)
        OBV[~con1 & con2] = -1 * self.volume
        OBV[~con1 & ~con2] = 0
        return -1 * ts_sum(OBV, 12)

    def gfalpha62(self):
        M = 10
        con1 = self.close > delay(self.close, 1)
        return -1 * ts_sum(con1, M) / M * 100

    def gfalpha63(self):
        M = 16
        con1 = self.close > delay(self.close, 1)
        return -1 * ts_sum(con1, M) / M * 100

    def gfalpha65(self):
        N = 1
        return (self.close - delay(self.close, N)) / delay(self.close,N)*self.volume

    def gfalpha66(self):
        N = 6
        return (self.close - delay(self.close, N)) / delay(self.close,N)*self.volume

    def gfalpha67(self):
        N = 12
        return (self.close - delay(self.close, N)) / delay(self.close,N)*self.volume

    def gfalpha68(self):
        m = 6
        p1 = 4
        p2 = 8
        RC = self.close / delay(self.close, m)
        ARC1 = SMA(delay(RC, 1), m, 1)
        DIF = MEAN(delay(ARC1, 1), p1) - MEAN(delay(ARC1, 1), p2)
        RCCD = SMA(DIF, m, 1)

    def gfalpha69(self):
        m = 6
        return self.close/delay(self.close,m)

    def gfalpha70(self):
        N = 6
        return (self.close-delay(self.close,N))/delay(self.close,N)*100

    def gfalpha71(self):
        N = 12
        return (self.close-delay(self.close,N))/delay(self.close,N)*100

    def gfalpha72(self):
        N1 = 6
        LC = delay(self.close, 1)
        return SMA(MAX(self.close - LC, 0), N1, 1) / SMA(abs(self.close - LC), N1, 1) * -100

    def gfalpha73(self):
        N1 = 12
        LC = delay(self.close, 1)
        return SMA(MAX(self.close - LC, 0), N1, 1) / SMA(abs(self.close - LC), N1, 1) * -100

    def gfalpha74(self):
        N1 = 24
        LC = delay(self.close, 1)
        return SMA(MAX(self.close - LC, 0), N1, 1) / SMA(abs(self.close - LC), N1, 1) * -100

    def gfalpha75(self):
        N = 8
        UP = self.temp
        UP[self.close > delay(self.close, 1)] = stddev(self.close, N)
        UP[self.close <= delay(self.close, 1)] = 0
        DOWN = self.temp
        DOWN[self.close <= delay(self.close, 1)] = stddev(self.close, N)
        DOWN[self.close > delay(self.close, 1)] = 0
        AUP = SMA(UP, N, 1)
        ADOWN = SMA(DOWN, N, 1)
        return -1 * AUP / (AUP + ADOWN) * 100

    def gfalpha76(self):
        N = 8
        UP = self.temp
        UP[self.close > delay(self.close, 1)] = stddev(self.close, N)
        UP[self.close <= delay(self.close, 1)] = 0

        AUP = SMA(UP, N, 1)

        return -1 * AUP

    def gfalpha77(self):
        N = 8

        DOWN = self.temp
        DOWN[self.close <= delay(self.close, 1)] = stddev(self.close, N)
        DOWN[self.close > delay(self.close, 1)] = 0

        ADOWN = SMA(DOWN, N, 1)
        return -1 * ADOWN

    def gfalpha78(self):
        m = 1
        a = self.temp
        con1 = self.close < delay(self.close, m)
        a[con1] = (self.close - delay(self.close, m)) / delay(self.close, m)
        con2 = self.close==delay(self.close, m)
        a[~con1 & con2] = 0
        a[~con1 & ~con2] = (self.close - delay(self.close, m)) / self.close
        return -1 * a

    def gfalpha79(self):
        N1 = 8
        LC = delay(self.close, 1)
        RSI = SMA(MAX(self.close - LC, 0), N1, 1) / SMA(abs(self.close - LC), N1, 1) * 100
        return (RSI - ts_min(RSI, N1)) / (ts_max(RSI, N1) - ts_min(RSI, N1))

    def gfalpha80(self):
        n = 8
        return 3 * WMA(log(self.close),n) + 3*WMA(WMA(log(self.close),n)) + WMA(WMA(WMA(log(self.close),n)))

    def gfalpha81(self):
        return (WMA(WMA(WMA(log(self.close),1),1),1) - delay(WMA(WMA(WMA(log(self.close),1),1),1), 1)) / delay(WMA(WMA(WMA(log(self.close),1),1),1), 1)

    def gfalpha83(self):
        n = 6
        r = self.close / ts_max(self.close) -1
        return sqrt(MEAN(ts_sum(r ** 2, n)))

    def gfalpha84(self):
        N1 = 4
        N2 = 8
        N3 = 12
        TH = MAX(self.high, delay(self.close, 1))
        TL = MIN(self.low, delay(self.close, 1))
        ACC1 = (self.close - SUM(TL, N1)) / SUM(TH - TL, N1)
        ACC2 = (self.close - SUM(TL, N2)) / SUM(TH - TL, N2)
        ACC3 = (self.close - SUM(TL, N3)) / SUM(TH - TL, N3)
        UOS = (ACC1 * N2 * N3 + ACC2 * N1 * N3 + ACC3 * N1 * N2) * 100 / (N1 * N2 + N1 * N3 + N2 * N3)
        return UOS

    def gfalpha85(self):
        return WMA(self.volume, 8)

    def gfalpha86(self):
        S = 4
        P = 8
        M = 6
        DIFF = WMA(self.volume, S) - WMA(self.volume, P)
        DEA = WMA(DIFF, M)
        VMACD = DIFF - DEA
        return VMACD

    def gfalpha87(self):
        M = 4
        P = 8
        S = 6
        VOSC = (MEAN(self.volume, M) - MEAN(self.volume, P)) / MEAN(self.volume, S) * 100
        return VOSC

    def gfalpha88(self):
        M = 4
        return (self.volume-delay(self.volume,M))/delay(self.volume,M)*100

    def gfalpha89(self):
        M = 6
        VRSI = SMA(MAX(self.volume - delay(self.volume, 1), 0), M, 1) / SMA(abs(self.volume - delay(self.volume, 1)), M, 1) * 100
        return VRSI

    def gfalpha90(self):
        M = 6
        LC = delay(self.close, 1)
        a = self.temp
        a[self.close > LC] = self.volume
        a[self.close <= LC] = 0
        b = self.temp
        b[self.close > LC] = 0
        b[self.close <= LC] = self.volume
        VR = SUM(a, M) / SUM(a, M) * 100
        return VR

    def gfalpha91(self):
        return stddev(self.volume, 8)

    def gfalpha92(self):
        return stddev(self.volume, 16)

    def gfalpha93(self):
        N = 8
        P1 = 8
        RSV = (ts_max(self.high, N) - self.close) / (ts_max(self.high, N) - ts_min(self.low, N)) * 100
        return SMA(RSV, P1, 1)

    def gfalpha94(self):
        N = 4
        P1 = 4
        RSV = (ts_max(self.high, N) - self.close) / (ts_max(self.high, N) - ts_min(self.low, N)) * 100
        return SMA(RSV, P1, 1)

    def gfalpha95(self):
        N = 12
        P1 = 12
        RSV = (ts_max(self.high, N) - self.close) / (ts_max(self.high, N) - ts_min(self.low, N)) * 100
        return SMA(RSV, P1, 1)

    def gfalpha96(self):
        M = 6
        return MEAN(abs(self.close - MEAN(self.close, M)), M)

    def gfalpha97(self):
        return stddev(self.amount, 8)

    def gfalpha98(self):
        return stddev(self.amount, 16)





