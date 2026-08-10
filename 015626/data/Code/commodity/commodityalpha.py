import os
import sys
import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt
from skimage.util import view_as_windows
import ts_eval.SIF_Factor_Test_com2 as com
from utils.operators_cc import *
from utils.rolling_adj import *
from utils.operators_wsc import *


def rolling_normalize(sig, window = 100):
    sig_max = sig.rolling(window,min_periods=int(window/2)).max()
    sig_min = sig.rolling(window,min_periods=int(window/2)).min()
    return ((sig-sig_min)/(sig_max-sig_min))*2-1

class FactorGeneratorComplex1:
    __data__ = None

    def __init__(self, factor_name='test', lookback_bars=5000, required_columns=None,
                 savepath='/dfs/user/012398/data/alpha/CHINA_FUTURES/MINUTE_5/'):
        self.factor_name = factor_name
        self.lookback_bars = lookback_bars
        self.required_columns = required_columns
        self.savepath = savepath


class trm(FactorGeneratorComplex1):
    def __init__(self):
        required_columns = ['high','low','close','main_mask']
        super(trm,self).__init__(required_columns = required_columns)

    def on_bar(self, data):
        hh = data['high'].rolling(30,min_periods = 10).max()
        ll = data['low'].rolling(30,min_periods = 10).min()
        cls = data['close']
        fac = 2 * cls/(hh + ll)
        fac = fac[data['main_mask']].mean(axis=1)
        sig = ts_rank(fac, 1500)
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)
       
class mom_etc(FactorGeneratorComplex1):
    def __init__(self):
        required_columns = ['high','low','close','main_mask']
        super(mom_etc,self).__init__(required_columns = required_columns)

    def on_bar(self, data):
        fac = data['close']
        fac = rolling_normalize(fac, window = 60)
        fac = fac.rolling(5,min_periods=5).mean()
        sig = fac[data['main_mask']].mean(axis=1)
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)

class lmrt(FactorGeneratorComplex1):
    def __init__(self):
        required_columns = ['close','main_mask']
        super(lmrt,self).__init__(required_columns = required_columns)

    def on_bar(self, data):
        rt0 = data['close']/data['close'].shift(1)-1
        fac = rt0.rolling(30,min_periods = 15).mean()
        fac = fac[data['main_mask']].mean(axis=1)
        sig = ts_rank(fac,1500)
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)

class rs_mod(FactorGeneratorComplex1):
    def __init__(self):
        required_columns = ['close','main_mask']
        super(rs_mod,self).__init__(required_columns = required_columns)
    def on_bar(self, data):
        rt0 = data['close']/data['close'].shift(1)-1
        rt0 = rt0[data['main_mask']].mean(axis=1)
        rt1 = rt0.copy()
        rt1[rt1<0] = 0
        N = 30
        A = ts_decay_linear(rt1, N, weight=None)
        B = ts_decay_linear(rt0.abs(),N, weight = None)
        fac = A/B
        sig = ts_rank(fac, 1500)
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)
        
class trm_mod(FactorGeneratorComplex1):
    def __init__(self):
        required_columns = ['high','low','close','main_mask']
        super(trm_mod,self).__init__(required_columns = required_columns)

    def on_bar(self, data):
        cls_ema = ts_truncated_ema_1(data['close'],60,alpha = 0.7)
        hh = data['high'].rolling(30,min_periods = 10).max()
        ll = data['low'].rolling(30,min_periods = 10).min()
        fac = 2 * cls_ema/(hh + ll)
        fac = fac[data['main_mask']].mean(axis=1)
        sig = ts_rank(fac, 1500)
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)

class trm_mod4(FactorGeneratorComplex1):
    def __init__(self):
        required_columns = ['high','low','close','BidAskSpreadMean','main_mask']
        super(trm_mod4,self).__init__(required_columns = required_columns)

    def on_bar(self, data):
        mask = data['main_mask']        
        coef_temp = data['close'].diff().rolling(30,min_periods = 1).std()# / r(data['BidAskSpreadMean'].rolling(30,min_periods = 1).mean().copy()))[data['main_mask']].mean(axis = 1)
        coef_temp = data['close'].diff().rolling(30,min_periods = 1).std()[data['main_mask']].sum(axis=1)
        coef = coef_temp.copy()
        coef[coef_temp >= 0.0015] = 0.5
        coef[(coef_temp < 0.0015)&(coef_temp > 0.0008)] = 1
        coef[coef_temp <= 0.0008] = 2        
        aa = 30        
        hh = data['high'].apply(lambda x:rolling_max_adj(x,coef,aa))
        ll = data['low'].apply(lambda x:rolling_min_adj(x,coef,aa))
        cls = data['close']
        fac = 2 * cls/(hh + ll)
        fac = fac[data['main_mask']].mean(axis=1)
        sig = ts_rank(fac, 1500)
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)
class crr(FactorGeneratorComplex1):
    def __init__(self):
        required_columns = ['close','main_mask']
        super(crr,self).__init__(required_columns = required_columns)

    def on_bar(self, data):
        cls = data['close']
        fac = cls.rolling(50,min_periods=25).apply(lambda x: x.corr(pd.Series(sorted(x),index=x.index)))
        sig = fac[data['main_mask']].sum(axis=1)
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)

class mom_avgline(FactorGeneratorComplex1):
    def __init__(self):
        required_columns = ['close','main_mask']
        super(mom_avgline,self).__init__(required_columns = required_columns)

    def on_bar(self, data):
        cls = data['close']
        avg1 = cls.rolling(10).mean()
        avg2 = cls.rolling(300).mean()
        avg3 = cls.rolling(600).mean()
        avg4 = cls.rolling(1200).mean()
        avg5 = cls.rolling(2400).mean()
        up = ((avg1 > avg2)&(avg2>avg3)&(avg3>avg4)&(avg4>avg5)).astype(int)
        down = ((avg1 < avg2)&(avg2<avg3)&(avg3<avg4)&(avg4<avg5)).astype(int)
        fac = (up - down).rolling(10).mean()
        sig = fac[data['main_mask']].sum(axis=1)
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)