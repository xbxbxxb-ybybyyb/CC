# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 17:34:11 2021

@author: appadmin
"""
import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

class cd_ind_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close', 'open']}
    normalize_size = 4800
    normalize_type = 'rolling_norm'
    num_range = '(-0, 1]'
    
    def calculate(self, data):
        
        hclose = data['close_000300.SH'].values[-62:]

        factor = np.diff(bk.move_mean(hclose, 60))
        
        return factor[-1]
    

class CPLR_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 242*2
    normalize_type = 'ts_rank'
    #num_range = '(-0, 1]'
    
    def calculate(self, data):
        
        hclose = data['close_000300.SH'].values[-116:]
        temp = bk.move_max(hclose, 40, min_count = 20)
        x = np.array(range(len(temp)))
        factor = rolling_linear_reg(x, temp, 75)
        
        return factor[-1]


class ClMaxClMin_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 10
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close', 'open']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = '(-0, 1]'
    
    def calculate(self, data):
        
        hclose = data['close_cont_IC'].values[-2000:]
        factor0 = bk.move_max(hclose, 40, min_count = 30)/bk.move_min(hclose, 40, min_count = 30)

        factor1 = rolling_norm(factor0, 242*2, method = 'ts_rank')

        factor = bk.move_mean(factor1, 2, min_count = 1)
        
        return factor[-1]
    
    
class CloseVoltoMean_ICIF_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 10
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close', 'open']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        
        hclose = data['close_000905.SH'].values[-50:]
        factor0 = bk.move_std(hclose, 30, min_count = 15)/bk.move_mean(hclose, 30, min_count = 15)

        factor = np.nanmean(factor0[-15:])
   
        return factor
    

class Crossing_Turns_ICIF_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 10
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close', 'open', 'high', 'low', 'vwap']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        
        hclose = (data['close_cont_IC'].values)[-1000:]
        hopen = (data['open_cont_IC'].values)[-1000:]
        hhigh = (data['high_cont_IC'].values)[-1000:]
        hlow = (data['low_cont_IC'].values)[-1000:]
        hvwap = (data['vwap_cont_IC'].values)[-1000:]
        
        temp = np.abs((np.where(hopen-hclose== 0, 0.1, hopen-hclose)))

        temp0 = hhigh - hlow

        temp1 = temp0/temp
        temp1[temp1>1000000] = np.nan
        shift_1 = shift(hvwap, 1)
        shift_1[shift_1==0] = np.nan
        a = bk.move_sum((hvwap/shift_1-1), 30, min_count = 15)
        vwtc_r = bk.move_mean(temp1*(a), 25, min_count = 5)

        factor = ts_rank(vwtc_r, 242*3)
        factor = np.nanmean(factor[-2:])
        if factor<=-0.5:
            factor = np.nan
        
        return factor
    

class GA_ind_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close', 'high', 'low', 'open']} 
    normalize_size = 3 * 242
    normalize_type = 'ts_rank'
    num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        n = 120
        hclose = (data['close_000300.SH'].values)[-150:]
        hhigh = (data['high_000300.SH'].values)[-150:]
        hlow = (data['low_000300.SH'].values)[-150:]
        hopen = (data['open_000300.SH'].values)[-150:]
        a = np.nanmax(hhigh[-n:])-shift(hopen, n)[-1]
        b = hclose[-1] - np.nanmin(hlow[-n:])
        c = (np.nanmax(hhigh[-n:])-np.nanmin(hlow[-n:]))*2
        if abs(c) < 1e-8:
            c = np.nan 
        factor = (a*b)/c
        return factor
    

class HHLS_ind_ICIF_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']} 
    normalize_size = 5 * 240
    normalize_type = 'rolling_norm'
    #num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        
        hhigh = (data['high_000905.SH'].values)[-120:]
        factor = np.nanmax(hhigh[-50:]) - np.nanmax(shift(hhigh, 50)[-50:])

        return factor


class HL123_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['close', 'high', 'low', 'open']} 
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        
        hhigh = (data['high_cont_IF'].values)[-120:]
        hlow = (data['low_cont_IF'].values)[-120:]
        
        i11 = bk.move_max(hhigh, 10, min_count = 5) - bk.move_min(hlow, 60, min_count = 10)
        shift_low = shift(hlow,30)
        shift_high = shift(hhigh, 30)
        shift_low[shift_low==0] = np.nan
        shift_high[shift_high == 0]=np.nan
        i12 = bk.move_max(shift_high, 10, min_count = 5) - bk.move_min(shift_low, 60, min_count = 10)
        #print(bk.move_min(shift_low, 60, min_count = 10)[-1])
        factor = np.nanmean((i11-i12)[-20:])

        return factor
    
    

class HL123_ICIF_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low', 'open']} 
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        hlow = (data['low_cont_IC'].values)[-120:]
        hhigh = (data['high_cont_IC'].values)[-120:]
        i11 = bk.move_max(hhigh, 10, min_count = 5) - bk.move_min(hlow, 60, min_count = 10)
        shift_low = shift(hlow,30)
        shift_high = shift(hhigh, 30)
        shift_low[shift_low==0] = np.nan
        shift_high[shift_high == 0]=np.nan
        i12 = bk.move_max(shift_high, 10, min_count = 5) - bk.move_min(shift_low, 60, min_count = 10)
        #print(bk.move_min(shift_low, 60, min_count = 10)[-1])
        factor = np.nanmean((i11-i12)[-20:])
        return factor



class HLDL2_ind_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low', 'open']} 
    data_dict['Index_Id'] = {'000300.SH':['close', 'high', 'low', 'open']}
    normalize_size = 5 * 240
    normalize_type = 'rolling_norm'
    num_range = '[-0, 1]'
    
    def calculate(self, data):
        hlow = (data['low_000300.SH'].values)[-120:]
        hhigh = (data['high_000300.SH'].values)[-120:]
        t_pcorr = (np.diff(hhigh)+np.diff(hlow))
        factor = np.nanmean(t_pcorr[-90:])
        return factor



class HLTM_Aug_ind_ICIF_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low', 'open']} 
    data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 5 * 242
    normalize_type = 'ts_rank'
    #num_range = '[-0, 1]'
    
    def calculate(self, data):
        hlow = (data['low_000905.SH'].values)[-90:]
        hhigh = (data['high_000905.SH'].values)[-90:]
        hclose = (data['close_000905.SH'].values)[-90:]
        hvolume = (data['volume_000905.SH'].values)[-90:]
        
        temp1 = bk.move_max(hhigh, 15, min_count = 7) - hclose
        
        #temp2 = data['close_spot']-data['low_spot'].rolling(15, min_periods = 7).min()
        temp2 = hclose - bk.move_min(hlow, 15, min_count = 7)
        
        temp = np.where(temp1>temp2, temp1, temp2)

        factor = np.nanmean((temp*hvolume)[-35:])
        return factor
    

class HcorrC_ind_ICIF_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low', 'open']} 
    data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    #num_range = '[-0, 1]'
    
    def calculate(self, data):

        high = data['high_000905.SH'].iloc[-120:]
        close = data['close_000905.SH'].iloc[-120:]
        factor = high.rolling(45, min_periods = 30).corr(close)
        factor[abs(factor>10)] = np.nan
        factor = np.nanmean(factor.iloc[-30:])
        return factor
    

class ICIF1_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low', 'open']} 
    #data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 0
    normalize_type = 'ts_rank'
    #num_range = '[-0, 1]'
    
    def calculate(self, data):

        hclose = data['close_cont_IC'].iloc[-1230:]
        temp5 = bk.move_mean(hclose, 5, min_count = 2)
        temp10 = bk.move_mean(hclose, 10, min_count = 5)
        temp20 = bk.move_mean(hclose, 20, min_count = 10)
        temp60 = bk.move_mean(hclose, 60, min_count = 30)
        temp120 = bk.move_mean(hclose, 120, min_count = 60)
        
        temp5_diff = (np.diff(temp5)>0).astype(int)
        temp10_diff = (np.diff(temp10)>0).astype(int)
        temp20_diff = (np.diff(temp20)>0).astype(int)
        temp60_diff = (np.diff(temp60)>0).astype(int)
        temp120_diff = (np.diff(temp120)>0).astype(int)
        factor = ts_rank(bk.move_mean(temp5_diff+temp10_diff+temp20_diff+temp60_diff+temp120_diff, 15, min_count = 5))
        factor = np.nanmean(factor.iloc[-10:])
        return factor
    
    

class ICIF4_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low', 'open']} 
    data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    num_range = '(-0.5, 1]'
    
    def calculate(self, data):

        hclose = data['close_000905.SH'].values[-62:]
        temp = np.nanmean(hclose[-60:]) - np.nanmean(shift(hclose, 20)[-40:])
        factor = np.abs(temp)
        return factor
    

class L123_ICIF_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low', 'open']} 
    #data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    num_range = '(-0.5, 1]'
    
    def calculate(self, data):

        hlow = (data['low_cont_IC'].values)[-90:]
        i11 = bk.move_min(hlow, 10, min_count = 5) - bk.move_min(hlow, 25, min_count = 10)
        i12 = bk.move_min(hlow, 20, min_count = 15) - bk.move_min(hlow, 30, min_count = 10)
        i2 = bk.move_mean((i11-i12), 30, min_count = 20)

        return i2[-1]
    

class L123_ind_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low', 'open']} 
    data_dict['Index_Id'] = {'000300.SH':['low']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    #num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        hlow = (data['low_000300.SH'].values)[-90:]
        i11 = bk.move_min(hlow, 10, min_count = 5) - bk.move_min(hlow, 25, min_count = 10)
        i12 = bk.move_min(hlow, 20, min_count = 15) - bk.move_min(hlow, 30, min_count = 10)
        i2 = np.nanmean((i11-i12)[-60:])
        return i2
    
    
class LCCorr_ind_ICIF_CC_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 12
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low', 'open']} 
    data_dict['Index_Id'] = {'000905.SH':['close', 'low']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    #num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        high = data['low_000905.SH'].iloc[-1300:]
        close = data['close_000905.SH'].iloc[-1300:]
        temp = high.rolling(60, min_periods = 30).corr(close)
        temp[abs(temp)>100] = np.nan
        factor = bk.move_mean(temp, 5, min_count = 2)

        factor = rolling_norm(factor, method = 'ts_rank')
        return factor[-1]
    
    

class LMLS_ind_ICIF_CC_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['low']} 
    #data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        low = data['low_cont_IC'].values[-90:]
        factor = np.nanmean(low[-75:]) - np.nanmean(shift(low, 30)[-45:])
        return factor


class LRS_max_CC_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['vwap']} 
    #data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 500
    normalize_type = 'ts_rank'
    #num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        vwap = data['vwap_cont_IC'].values[-150:]
        temp1 = bk.move_max(vwap, 50, min_count = 20)
        x = np.array(range(len(vwap)))
        factor = (rolling_linear_reg(x, temp1, 50))
        return factor[-1]
    

class LminC_ind_CC_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IC':['vwap']} 
    data_dict['Index_Id'] = {'000300.SH':['close', 'low']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = '[-0.8, 1]'
    
    def calculate(self, data):
        
        low = data['low_000300.SH'].values[-180:]
        
        return -np.nanmin(low)/(data['close_000300.SH'].values[-1])


class LminLmean_CC_ICIF_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['low']} 
    #data_dict['Index_Id'] = {'000300.SH':['close', 'high', 'low', 'open']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = '[-0.8, 1]'
    
    def calculate(self, data):
        
        low = data['low_cont_IC'].values[-60:]
        
        return -np.nanmin(low)/np.nanmean(low[-30:])



class LminLmean_ind_CC_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IC':['low']} 
    data_dict['Index_Id'] = {'000300.SH':['close', 'high', 'low', 'open']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = '[-0.8, 1]'
    
    def calculate(self, data):
        
        low = data['low_000300.SH'].values[-45:]
        
        return -np.nanmin(low)/np.nanmean(low[-25:])
    
    
class MALS_ICIF_CC_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IC':['low']} 
    data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 242*2
    normalize_type = 'ts_rank'
    num_range = '[-0.5, 1]'
    
    def calculate(self, data):
        
        low = data['low_000905.SH'].values[-75:]
        factor = bk.move_mean(low, 75, min_count = 15) - bk.move_mean(shift(low, 15), 60, min_count = 7)
        
        return factor[-1]


class RolTrendLS_CC_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['close', 'high', 'low', 'open']} 
    #data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = '[-0.5, 1]'
    
    def calculate(self, data):
        hclose = (data['close_cont_IF'].values)[-150:]
        hhigh = (data['high_cont_IF'].values)[-150:]
        hlow = (data['low_cont_IF'].values)[-150:]

        ll = hclose-bk.move_min(hlow, 120, min_count = 15) - (bk.move_max(hhigh, 120, min_count = 15) - bk.move_min(hlow, 60, min_count = 15))
        a2 = bk.move_mean(ll, 10, min_count = 5)
        a3 = np.nanmean(a2[-10:])
        vwtc_r = 3*a3-2*a2[-1]
        return vwtc_r
    

class RolTrendLS_ind_CC_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IF':['close', 'high', 'low', 'open']} 
    data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = '[-0.5, 1]'
    
    def calculate(self, data):
        hclose = (data['close_000905.SH'].values)[-100:]
        hhigh = (data['high_000905.SH'].values)[-100:]
        hlow = (data['low_000905.SH'].values)[-100:]
        temp = (bk.move_max(hhigh, 60, min_count = 15) - bk.move_min(hlow, 60, min_count = 15))
        temp[abs(temp)<0.00001] = np.nan
        ll = (hclose-bk.move_min(hlow, 60, min_count = 15)) / temp
        a2 = bk.move_mean(ll, 10, min_count = 5)
        a3 = bk.move_mean(a2, 10, min_count = 5)
        vwtc_r = 3*a3-2*a2
        
        return np.nanmean(vwtc_r[-5:])
    
    
class SLCS_CC_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 7
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IF':['close', 'high', 'low', 'open']} 
    data_dict['Index_Id'] = {'000300.SH':['close', 'high', 'low', 'open']}
    normalize_size = 242*4
    normalize_type = 'ts_rank'
    num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        close_spot = (data['close_000300.SH'].values)[-1290:]
        ind = list(range(len(close_spot)))
        m_vwap_ind_r = rolling_linear_reg(ind, close_spot, 60)
        factor = rolling_norm(m_vwap_ind_r, method = 'ts_rank')
        factor[factor<=-0.5] = np.nan

        return factor[-1]


class SLHS_CC_ICIF_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 20
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IF':['close', 'high', 'low', 'open']} 
    data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        high_spot = (data['high_000905.SH'].values)[-2730:]
        ind = list(range(len(high_spot)))
        m_vwap_ind_r = rolling_linear_reg(ind, high_spot, 60)
        factor = ts_rank(m_vwap_ind_r, 1200)
        factor[factor<=-0.5] = np.nan
        factor = ts_rank(factor, 242*6)
        
        return factor[-1]
    
        
class SYXWR_ind_CC_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IF':['close', 'high', 'low', 'open']} 
    data_dict['Index_Id'] = {'000300.SH':['close', 'high', 'low', 'open']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        hopen = (data['open_000300.SH'].values)[-150:]
        hhigh = (data['high_000300.SH'].values)[-150:]
        hlow = (data['low_000300.SH'].values)[-150:]
        hclose = (data['close_000300.SH'].values)[-150:]
        
        temp1 = np.where(hopen>hclose, hopen, hclose)
        
        a = bk.move_mean((hhigh - temp1), 35, min_count = 15)
        b = bk.move_max(hhigh, 35, min_count = 15) - bk.move_min(hlow, 35, min_count = 15)
        a[abs(a)<1e-8] = np.nan
        b[abs(b) < 1e-8] = np.nan
        t_pcor = (hhigh-temp1)/a
        
        t_pcor2 = (hclose-bk.move_min(hlow, 35, min_count = 15))/b

        return np.nanmean((t_pcor2 - t_pcor)[-60:])
    

class VMaxVmean_CC_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low', 'open']} 
    #data_dict['Index_Id'] = {'000300.SH':['close', 'high', 'low', 'open']}
    normalize_size = 480
    normalize_type = 'ts_rank'
    #num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        vwap = (data['vwap_cont_IC'].values)[-61:]
        factor = np.nanmax(vwap[-60:])/np.nanmin(vwap[-60:])

        return factor

class hhll_ind_CC_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low', 'open']} 
    data_dict['Index_Id'] = {'000300.SH':['close', 'high', 'low', 'open']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = '(-0.5, 1]'
    
    def calculate(self, data):
       
        hhigh = data['high_000300.SH'].iloc[-121:]
        hlow = data['low_000300.SH'].iloc[-121:]
        temp = np.where((hhigh>hhigh.shift(1)) & (hlow>hlow.shift(1)), 4, np.where((hhigh<hhigh.shift(1)) & (hlow<hlow.shift(1)), 0, 1))
        
        return np.abs(np.nanmean(temp[-120:]))


class BS_7_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_superorder_money', 'buy_bigorder_money', 'amount']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        
        buy_superorder_money_500 = data['buy_superorder_money'].iloc[-20:].fillna(0).values
        buy_bigorder_money_500 = data['buy_bigorder_money'].iloc[-20:].fillna(0).values
        amount = data['amount'].iloc[-20:].values
        factor = (buy_superorder_money_500+buy_bigorder_money_500)/amount

        factor[abs(factor)>100000] = np.nan

        factor = np.nanmean(factor, axis = 0)
            
        return np.nanmean(factor)


class BS_Main2_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['SellUniqueOrderNum', 'BuyUniqueOrderNum', 'close']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '[0, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        hclose = data['close'].iloc[-45:].values
        amount = data['amount'].iloc[-13:]
        
        df_s = amount.rolling(10, min_periods = 5).sum()
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0).values[-2:].astype(float)
        bool_df[bool_df == 0] = np.nan
        
        SellUniqueOrderNum = data['SellUniqueOrderNum'].iloc[-43:].values
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].iloc[-43:].values
        a = bk.move_sum((SellUniqueOrderNum + BuyUniqueOrderNum), 40, min_count = 1, axis = 0)[-2:]
        b = (hclose[40:]/hclose[:-40]-1)[-2:]
        
        factor = np.nanmean(a*b*bool_df, axis = 1)
        
        factor = np.nansum(factor)
        return factor
    
    
class CFG29_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor', 'close']
    normalize_size = 400 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        hclose = data['close_preadj'].iloc[-75:].values
        temp1 = bk.move_max(hclose, 35, min_count = 20, axis = 0)[-36:]
        holder = {}
        for i, item in enumerate(temp1.T):
            x = np.array(range(len(item)))
            holder[i] = pd.Series(rolling_linear_reg(x, item, 35))
        
        factor = pd.DataFrame(holder).mean(axis = 1).iloc[-1]
        return factor


class CFG30_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','amount', 'close']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '[0, 1]'# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        hclose = data['close_preadj'].iloc[-46:].values
        hamount = data['amount'].iloc[-106:]
        
        df_s = hamount.rolling(60, min_periods = 15).sum()
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0).values[-45:].astype(float)
        bool_df[bool_df==0]=np.nan
        
        upclose = np.nansum(((hclose[1:]*bool_df)>(hclose[:-1]*bool_df)), axis = 1)
        downclose = np.nansum(((hclose[1:]*bool_df)<(hclose[:-1]*bool_df)), axis = 1)
        t_prcd2 = (upclose-downclose)/ (upclose+downclose)
        
        t_prcd2[abs(t_prcd2)>1000000] = np.nan
        
        factor = np.nanmean(t_prcd2)
        return factor


class CFG7_2_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','open', 'weight','close','turnover_rate']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        to = data['turnover_rate'].iloc[-180:].values
        hclose = data['close_preadj'].iloc[-181:].values
        hopen = data['open_preadj'].iloc[-181:].values
        
        df_s = data['weight'].iloc[-181:]
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0).values.astype(float)[-180:]
        bool_df[bool_df == 0] = np.nan
        
        ret = (hclose/hopen -1)[-180:]
        hret = hclose[1:]/hclose[:-1] -1
        
        ret[abs(ret)>100000] = np.nan
        hret[abs(hret)>100000] = np.nan
        
        a = (hclose<hopen).astype(float)[-180:]
        
        cc1 = (((to*a)/abs(ret*a)))
        cc1[abs(cc1) > 100000] = np.nan
        ccc1 = bk.move_mean(cc1, 90, min_count = 7, axis = 0)
        ccc1 = ccc1*bool_df
        hret = hret*bool_df
        ccc1 = pd.DataFrame(ccc1, index = data['close_preadj'].iloc[-180:].index, columns = data['close_preadj'].iloc[-180:].columns)
        hret = pd.DataFrame(hret, index = data['close_preadj'].iloc[-180:].index, columns = data['close_preadj'].iloc[-180:].columns)
        cc2 = to_ts(ccc1, hret).values
        ccc2 = np.nanmean(cc2[-90:])
        
        return ccc2
   
    
class CFG7_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','open', 'weight','close','turnover_rate']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        to = data['turnover_rate'].iloc[-180:].values
        hclose = data['close_preadj'].iloc[-181:].values
        hopen = data['open_preadj'].iloc[-181:].values
        
        ret = (hclose/hopen -1)[-180:]
        hret = hclose[1:]/hclose[:-1] -1
        
        ret[abs(ret)>100000] = np.nan
        hret[abs(hret)>100000] = np.nan
        
        a = (hclose<hopen).astype(float)[-180:]
        
        cc1 = (((to*a)/abs(ret*a)))
        cc1[abs(cc1) > 100000] = np.nan
        ccc1 = bk.move_mean(cc1, 90, min_count = 7, axis = 0)
        ccc1 = pd.DataFrame(ccc1, index = data['close_preadj'].iloc[-180:].index, columns = data['close_preadj'].iloc[-180:].columns)
        hret = pd.DataFrame(hret, index = data['close_preadj'].iloc[-180:].index, columns = data['close_preadj'].iloc[-180:].columns)
        cc2 = to_ts(ccc1, hret).values
        ccc2 = np.nanmean(cc2[-90:])
        
        return ccc2


class CFG8_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','open', 'volume','close', 'float_shares']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '(-0.5, 1]'# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        hvolume = data['volume_preadj'].iloc[-45:].values
        hclose = data['close_preadj'].iloc[-46:].values
        hfs = data['float_shares'].iloc[-45:].values
        
        hret = hclose[1:]/hclose[:-1] - 1
        d1 = hvolume/(hclose[-45:])/hfs
        
        hret[abs(hret)>100000] = np.nan
        d1[abs(d1)>100000] = np.nan
        
        d1 = pd.DataFrame(d1, index = data['close_preadj'].iloc[-45:].index, columns = data['close_preadj'].iloc[-45:].columns)
        hret = pd.DataFrame(hret, index = data['close_preadj'].iloc[-45:].index, columns = data['close_preadj'].iloc[-45:].columns)
        d1 = to_ts(d1, hret).values
        ccc2 = np.nanmean(d1)
        
        return ccc2

    
class ClMaxClMin_nr_wt_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close','turnover_rate']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
         
        stk_weight = data['weight'].values[-66:]
        tover = data['turnover_rate'].iloc[-66:]
        turnover = tover.rolling(60, min_periods = 15).mean()
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0).values
        mask = (stk_weight*temp4)[-5:]
        
        hclose = data['close_preadj'].values[-1265:]
        m_vwap_ind_r = bk.move_max(hclose, 45, min_count = 30, axis = 0)/bk.move_min(hclose, 45, min_count = 30, axis = 0)
        m_vwap_ind_r[np.abs(m_vwap_ind_r)>10000] = np.nan
        temp = rolling_norm(m_vwap_ind_r, 242*5)[-5:]
        tempdf = np.nanmean(np.nansum(temp*mask, axis = 1))
        
        return tempdf
    

class Crossing_Turns_tr_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','open', 'weight','close','turnover_rate', 'high', 'low']
    normalize_size = 1200 # normalize所用历史数据长度'
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        tover = data['turnover_rate'].iloc[-66:]
        turnover = tover.rolling(60, min_periods = 15).mean()
        turnover_rank = (2 * turnover.rank(axis=1, pct=True) - 1).values[-5:]

        hopen = data['open_preadj'].iloc[-63:].values
        hhigh = data['high_preadj'].iloc[-63:].values
        hclose = data['close_preadj'].iloc[-63:].values
        hlow = data['low_preadj'].iloc[-63:].values
        
        temp = np.abs(np.where(hopen-hclose == 0, 0.1, hopen-hclose))

        temp0 = (hhigh - hlow)
        temp1 = temp0/temp
        v1 = data['volume_preadj'].iloc[-64:].values
        v1[abs(v1) < 1e-8] = np.nan
        amount = data['amount'].iloc[-64:].values
        vwap = amount/v1
        a = bk.move_sum((vwap[1:]/vwap[:-1]-1), 30, min_count = 15, axis = 0)
        vwtc_r = bk.move_mean((temp1*(a)), 25, min_count = 5, axis = 0)[-5:]

        tempdf = np.nanmean(np.nanmean((vwtc_r*turnover_rank), axis = 1))

        return tempdf
    

class GA_ind_nr_tr_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 8
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','open', 'weight','close','turnover_rate', 'float_shares']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        tover = data['turnover_rate'].iloc[-66:]
        turnover = tover.rolling(60, min_periods = 15).mean()
        mask = (2 * turnover.rank(axis=1, pct=True) - 1).values[-5:]
        
        hopen = data['open_preadj'].iloc[-1340:].values
        hhigh = data['high_preadj'].iloc[-1340:].values
        hclose = data['close_preadj'].iloc[-1340:].values
        hlow = data['low_preadj'].iloc[-1340:].values
        
        h = bk.move_max(hhigh, 120, min_count = 60, axis = 0)[-1210:]
        l = bk.move_min(hlow, 120, min_count = 60, axis = 0)[-1210:]
        
        a = h-(hopen[:-120])[-1210:]
        b = hclose[-1210:] - l[-1210:]
        c = (h-l)*2
        c[abs(c) < 1e-8] = np.nan
        vwtc_r = (a+b)/c
        vwtc_r = rolling_norm(vwtc_r)[-5:]
        tempdf = np.nanmean(np.nansum(vwtc_r*mask, axis = 1))

        return tempdf

    

class HDLD_ae_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','open', 'close','turnover_rate', 'amount']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        amount = (data['amount_preadj']).iloc[-181:]
        turnover = data['turnover_rate'].iloc[-91:]
        df_s = (amount.rolling(120, min_periods = 15).sum())
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0).iloc[-60:].values
        ret_30 = (turnover/turnover.shift(30)-1)
        ret_30 = ret_30.replace([-np.inf, np.inf], np.nan)
        temp5 = ret_30.gt(pd.Series(ret_30.quantile(0.80, axis = 1)), axis=0).iloc[-60:].values

        bool_df = (temp1*temp5)

        
        hclose = data['close_preadj'].iloc[-65:].values
        hopen = data['open_preadj'].iloc[-65:].values        

        temp1 = (np.where(hopen>hclose, hopen, hclose))
        temp2 = (np.where(hopen>hclose, hclose, hopen))
        
        t_pcorr = (temp1[1:] - temp1[:-1]+temp2[1:] - temp2[:-1])[-60:]
        tempdf = np.nanmean(np.nansum(t_pcorr*bool_df, axis = 1))
        
        return tempdf


class HHLS_ar_CC_CFG_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','high','amount']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        stk_amount = (data['amount']).iloc[-5:]
        stk_amount_rank = 2 * stk_amount.rank(axis=1, pct=True) - 1
        mask = stk_amount_rank.values
        
        hhigh = data['high_preadj'].iloc[-56:].values
        hhigh_s = data['high_preadj'].iloc[-200:].shift(50).values[-56:]
        
        temp = (bk.move_max(hhigh, 50, min_count = 15, axis = 0) - bk.move_max(hhigh_s, 50, min_count = 15, axis = 0))[-5:]
        tempdf = np.nansum(temp*mask, axis = 1)

        factor = np.nanmean(tempdf)
        
        return factor
    

class L123_at_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','open', 'weight','close','turnover_rate', 'float_shares']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        tover = data['turnover_rate'].iloc[-91:]       
        turnover = (tover.rolling(60, min_periods = 15).mean()).iloc[-30:]
        amount = data['amount'].iloc[-151:]
        df_s = amount.rolling(120, min_periods = 15).sum().iloc[-30:]
        
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0).values
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0).values        
        mask = temp1*temp4
        
        hlow = data['low_preadj'].iloc[-61:].values
        i11 = (bk.move_min(hlow, 10, min_count = 5, axis = 0)-bk.move_min(hlow, 25, min_count = 10, axis = 0))
        i12 = bk.move_min(hlow, 20, min_count = 15, axis = 0)-bk.move_min(hlow, 30, min_count = 10, axis = 0)
        i2 = (i11-i12)[-30:]
        tempdf = np.nansum(i2*mask, axis = 1)
        factor = np.nanmean(tempdf)
        
        return factor
    

class L123_nr_ac_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','amount', 'stk_index_corr_hs300', 'low']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        amount = data['amount'].iloc[-166:]
        df_s = amount.rolling(120, min_periods = 15).sum().iloc[-45:]
        stk_index_corr = data['stk_index_corr_hs300'].iloc[-45:]        
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0).values
        temp2 = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.80, axis = 1)), axis=0).values
        mask = (temp1*temp2)
        
        hlow = data['low_preadj'].iloc[-1256:].values
        i11 = (bk.move_min(hlow, 10, min_count = 5, axis = 0)-bk.move_min(hlow, 25, min_count = 10, axis = 0))
        i12 = bk.move_min(hlow, 20, min_count = 15, axis = 0)-bk.move_min(hlow, 30, min_count = 10, axis = 0)
        i2 = (i11-i12)
        i2 = rolling_norm(i2, 242*5)[-45:]
        tempdf = np.nanmean(i2*mask, axis = 1)
        factor = np.nanmean(tempdf)
        
        return factor
    
    
class L123_nr_vt_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'turnover_rate', 'low']
    normalize_size = 720 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        tover = data['turnover_rate'].iloc[-101:]       
        turnover = (tover.rolling(60, min_periods = 15).mean()).iloc[-40:]
        
        stk_close = data['close_preadj'].iloc[-71:]
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = ts_std(stk_ret, 30).iloc[-40:]

        temp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0)
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)    
        mask = temp3*temp4
        
        hlow = data['low_preadj'].iloc[-1251:].values
        i11 = (bk.move_min(hlow, 10, min_count = 5, axis = 0)-bk.move_min(hlow, 25, min_count = 10, axis = 0))
        i12 = bk.move_min(hlow, 20, min_count = 15, axis = 0)-bk.move_min(hlow, 30, min_count = 10, axis = 0)
        i2 = (i11-i12)
        i2 = rolling_norm(i2, 242*5)[-40:]
        tempdf = np.nanmean(i2*mask, axis = 1)
        factor = np.nanmean(tempdf)
        
        return factor
    

class L123_nr_wv_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'weight', 'low']
    normalize_size = 2400 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        stk_weight = (data['weight_hs300']).iloc[-60:].values
        
        stk_close = data['close_preadj'].iloc[-91:]
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = ts_std(stk_ret, 30).iloc[-60:]
        
        temp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0)
        mask = stk_weight*temp3
        
        hlow = data['low_preadj'].iloc[-1261:].values
        i11 = (bk.move_min(hlow, 10, min_count = 5, axis = 0)-bk.move_min(hlow, 25, min_count = 10, axis = 0))
        i12 = bk.move_min(hlow, 20, min_count = 15, axis = 0)-bk.move_min(hlow, 30, min_count = 10, axis = 0)
        i2 = (i11-i12)
        i2 = rolling_norm(i2)[-60:]
        tempdf = np.nansum(i2*mask, axis = 1)
        factor = np.nanmean(tempdf)
        
        return factor
    


class HL123_nr_av_CC_CFG_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor', 'high','close','amount', 'low']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        hamount = data['amount'].iloc[-156:]
        df_s = hamount.rolling(120, min_periods = 15).sum()
        stk_close = data['close_preadj'].iloc[-65:]
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = ts_std(stk_ret, 30)
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0).values[-30:]
        temp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0).values[-30:]
        mask = (temp3*temp1)

        hlow = data['low_preadj'].iloc[-1274:]
        hhigh = data['high_preadj'].iloc[-1274:]

        hlow_s = hlow.shift(30).values
        hhigh_s = hhigh.shift(30).values

        hlow = hlow.values
        hhigh = hhigh.values

        i11 = bk.move_max(hhigh, 10, min_count = 5, axis = 0)-bk.move_min(hlow, 60, min_count = 10, axis = 0)
        i12 = bk.move_max(hhigh_s, 10, min_count = 5, axis = 0)-bk.move_min(hlow_s, 60, min_count = 10, axis = 0)
        i2 = (i11-i12)
        i2 = rolling_norm(i2, 242*5)[-30:]
        
        factor = np.nanmean(np.nansum(i2*mask, axis = 1))
        return factor



class LCCorr_nr_a3_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'amount', 'low']
    normalize_size = 2400 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        hamount = data['amount'].iloc[-136:]
        df_s = (hamount.rolling(120, min_periods = 15).sum())
        hclose = data['close_preadj'].iloc[-50:]
        
        ret = (hclose/hclose.shift(30)-1)
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0).values[-15:]
        temp6 = ret.gt(pd.Series(ret.quantile(0.80, axis = 1)), axis=0).values[-15:]    
        mask = temp1*temp6
        
        high = data['low_preadj'].iloc[-1322:]
        close = data['close_preadj'].iloc[-1322:]
        s = bk.move_std(high.values, 60, min_count = 30, axis = 0)
        f = bk.move_std(close.values, 60, min_count = 30, axis = 0)
        s[abs(s) < 1e-7] = np.nan
        f[abs(f) < 1e-7] = np.nan
        t_chgpcor2 = (high.rolling(60, min_periods=30).cov(close)).values / (s * f)
        t_chgpcor2 = rolling_norm(t_chgpcor2)[-15:]
        tempdf = np.nansum(t_chgpcor2*mask, axis = 1)
        factor = np.nanmean(tempdf)
        
        return factor
    
class LMLS_nr_t3_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'turnover_rate', 'low']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        tover = data['turnover_rate'].iloc[-80:]       
        turnover = (tover.rolling(60, min_periods = 15).mean()).iloc[-15:]
        hclose = data['close_preadj'].iloc[-70:]       
        ret = (hclose/hclose.shift(30)-1).iloc[-15:]
        
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0).values
        temp6 = ret.gt(pd.Series(ret.quantile(0.80, axis = 1)), axis=0).values   
        mask = (temp4*temp6).astype(float)
        
        hlow = data['low_preadj'].iloc[-1276:].values
        hlow_s = data['low_preadj'].iloc[-1322:].shift(15).values[-1276:]
        
        temp = bk.move_mean(hlow, 60, min_count = 15, axis = 0) - bk.move_mean(hlow_s, 45, min_count = 15, axis = 0)
        temp = rolling_norm(temp)[-15:]
        factor = np.nanmean(np.nansum(temp*mask, axis = 1))
        
        return factor


class Lma_te_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'turnover_rate', 'low']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        tover = data['turnover_rate'].iloc[-1330:]       
        temp = bk.move_mean(tover, 60, min_count = 15, axis = 0)
        turnover = pd.DataFrame(temp, index= tover.index, columns = tover.columns).iloc[-1220:]
        ret_30 = (tover/tover.shift(30)-1).iloc[-1220:]
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)
        temp5 = ret_30.gt(pd.Series(ret_30.quantile(0.80, axis = 1)), axis=0)     
        mask = temp4*temp5

        hlow = data['low_preadj'].iloc[-1330:]
        hclose = data['close_preadj'].iloc[-1330:]
        
        vwtc_r = (hlow-bk.move_mean((hclose), 120, min_count = 30, axis = 0))[-1220:]
        tempdf = np.nansum(vwtc_r*mask, axis = 1)
        
        factor = bk.move_mean(tempdf, 8, min_count = 2, axis = 0)
        factor = ts_rank(factor)
        factor = np.nanmean(factor[-3:])
        
        return factor
    
   
class LminC_nr_rl_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'turnover_rate', 'low']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '(0, 1]'# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        tover = data['turnover_rate'].iloc[-46:]          
        tover[abs(tover) < 1e-8] = np.nan
        ret_30 = (tover/tover.shift(30)-1).iloc[-15:]
        temp5 = ret_30.gt(pd.Series(ret_30.quantile(0.90, axis = 1)), axis=0)     
        mask = temp5

        hlow = data['low_preadj'].iloc[-1400:].values
        hclose = data['close_preadj'].iloc[-1400:].values
        
        lltc_ind_r = -bk.move_min(hlow, 180, min_count = 90, axis = 0)/hclose
        lltc_ind_r = rolling_norm(lltc_ind_r)[-15:]
        tempdf = (lltc_ind_r*mask)
        tempdf = np.nansum(tempdf, axis = 1)
        factor = np.nanmean(tempdf)
        
        return factor


class LminLmean_nr_as_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','amount', 'low']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        hamount = data['amount'].iloc[-130:]
        temp = bk.move_sum(hamount, 120, min_count = 15, axis = 0)
        df_s = pd.DataFrame(temp,index = hamount.index, columns = hamount.columns)
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)   
        mask = stk_amount[-8:]
        
        hlow = data['low_preadj'].iloc[-1275:]
        ctl_r = -bk.move_min(hlow, 60, min_count = 15, axis = 0)/bk.move_mean(hlow, 30, min_count = 10, axis = 0)
        
        lltc_ind_r = rolling_norm(ctl_r)[-8:]
        tempdf = np.nansum((lltc_ind_r*mask), axis = 1)

        factor = np.nanmean(tempdf)
        return factor


class LminLmean_nr_corrturn_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'turnover_rate', 'low', 'stk_index_corr_hs300']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        tover = data['turnover_rate'].iloc[-95:]
        temp = bk.move_mean(tover, 60, min_count = 15, axis = 0)
        turnover = pd.DataFrame(temp,index = tover.index, columns = tover.columns).iloc[-10:]
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0).values
        
        stkc = data['stk_index_corr_hs300'].iloc[-10:]
        temp2 = stkc.gt(pd.Series(stkc.quantile(0.80, axis = 1)), axis=0).values
        mask = temp4*temp2
        
        hlow = data['low_preadj'].iloc[-1280:]
        ctl_r = -bk.move_min(hlow, 60, min_count = 15, axis = 0)/bk.move_mean(hlow, 30, min_count = 10, axis = 0)
        
        lltc_ind_r = rolling_norm(ctl_r)[-10:]
        tempdf = np.nansum((lltc_ind_r*mask), axis = 1)

        factor = np.nanmean(tempdf)
        return factor


class RS_ind_wt_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'turnover_rate', 'weight']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        tover = data['turnover_rate'].iloc[-70:]
        temp = bk.move_mean(tover, 60, min_count = 15, axis = 0)
        turnover = pd.DataFrame(temp,index = tover.index, columns = tover.columns).iloc[-8:]
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0).values
        
        stk_weight = (data['weight']).iloc[-8:].values
        wt = stk_weight*temp4

        hclose = data['close_preadj'].iloc[-35:]
        ret = (hclose.values)[1:]/(hclose.values)[:-1]
        a = bk.move_std(ret, 25, min_count = 15, axis = 0)[-8:]
        a[abs(a)<1e-8] = np.nan     
        hclose_s = hclose.shift(24).iloc[-8:].values
        
        i1 = (((hclose.values)[-8:])/hclose_s-1) / a

        tempdf = np.nansum((i1*wt), axis = 1)

        factor = np.nanmean(tempdf)
        return factor


class SYXWR_nr_wt_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'weight','turnover_rate', 'low', 'high', 'open']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        tover = data['turnover_rate'].iloc[-105:]
        temp = bk.move_mean(tover, 60, min_count = 15, axis = 0)
        turnover = pd.DataFrame(temp,index = tover.index, columns = tover.columns).iloc[-45:]
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0).values
        
        stk_weight = (data['weight']).iloc[-45:].values
        mask = stk_weight*temp4

        hopen = data['open_preadj'].iloc[-75:].values
        hclose = data['close_preadj'].iloc[-75:].values 
        hhigh = data['high_preadj'].iloc[-75:].values
        hlow = data['low_preadj'].iloc[-75:].values 
        
        temp1 = (np.where(hopen>hclose, hopen, hclose))
        
        b = bk.move_mean((hhigh - temp1), 30, min_count = 15, axis = 0)
        b[abs(b)<1e-8] = np.nan
        t_pcor = (hhigh - temp1)/b
        h = bk.move_max(hhigh, 30, min_count = 15, axis = 0)
        l = bk.move_min(hlow, 30, min_count = 15, axis = 0)
        a = h-l
        t_pcor2 = (hclose-l)/a
        t_pcorr = np.nansum(((t_pcor2 - t_pcor)[-45:])*mask, axis = 1)
        
        factor = np.nanmean(t_pcorr)
        return factor



class ZHZH_vt_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'turnover_rate', 'high']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        tover = data['turnover_rate'].iloc[-75:]
        temp = bk.move_mean(tover, 60, min_count = 15, axis = 0)
        turnover = pd.DataFrame(temp,index = tover.index, columns = tover.columns).iloc[-15:]
        
        stk_close = data['close_preadj'].iloc[-50:]
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = ts_std(stk_ret, 30).iloc[-15:]
        
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0).values 
        temp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0).values
        mask = temp3*temp4

        hhigh = data['high_preadj'].iloc[-120:].values
        h = bk.move_max(hhigh, 10, min_count = 5, axis = 0)
        hc = bk.move_mean(((hhigh >= h).astype(int)), 90, min_count = 5, axis = 0)[-15:]
        
        factor = np.nanmean(np.nanmean(hc*mask, axis = 1))
        
        return factor



class cd_ind_nr_at_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'turnover_rate', 'amount']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        tover = data['turnover_rate'].iloc[-75:]
        hamount = data['amount'].iloc[-135:]
        
        temp = bk.move_mean(tover, 60, min_count = 15, axis = 0)
        tempp = bk.move_sum(hamount, 120, min_count = 15, axis = 0)
        turnover = pd.DataFrame(temp,index = tover.index, columns = tover.columns).iloc[-10:]
        df_s = pd.DataFrame(tempp,index = hamount.index, columns = hamount.columns).iloc[-10:]
        
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0).values
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0)

        mask = temp1*temp4
        
        hclose = data['close_preadj'].iloc[-1280:].values
        
        hmean = bk.move_mean(hclose, 60, min_count = 2, axis = 0)
        htemp = hmean[1:] - hmean[:-1]
        
        htemp = rolling_norm(htemp, 242*5)[-10:]
        tempdf = np.nansum(htemp*mask, axis = 1)
        factor = np.nanmean(tempdf)
        return factor



class hhll_ind_nr_as_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'amount', 'low', 'high']
    normalize_size = 2400 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
           
        hamount = data['amount'].iloc[-185:]
        tempp = bk.move_sum(hamount, 120, min_count = 15, axis = 0)
        df_s = pd.DataFrame(tempp,index = hamount.index, columns = hamount.columns).iloc[-60:]
        
        mask = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        
        hhigh = data['high_preadj'].iloc[-1275:].values
        hlow = data['low_preadj'].iloc[-1275:].values
        
        d1 = (hhigh[1:]>hhigh[:-1])
        d2 = (hlow[1:]>hlow[:-1])
        
        d_f = (d1.astype(int)+d2.astype(int))
        d_f[d_f == 2] = 4
        
        factor1 = rolling_norm(d_f, 242*5)[-60:]

        factor = np.nansum(factor1*mask, axis = 1)
        
        factor = np.nanmean(factor)

        return factor



class hhll_nr_we_CC_CFG_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','weight', 'turnover_rate', 'low', 'high']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        tover = data['turnover_rate'].iloc[-95:]          
        tover[abs(tover) < 1e-8] = np.nan
        ret_30 = (tover/tover.shift(30)-1).iloc[-60:]
        temp5 = ret_30.gt(pd.Series(ret_30.quantile(0.80, axis = 1)), axis=0)
        stk_weight = (data['weight']).iloc[-60:].values
        
        mask = temp5*stk_weight
        
        hhigh = data['high_preadj'].iloc[-1275:].values
        hlow = data['low_preadj'].iloc[-1275:].values
        
        d1 = (hhigh[1:]>hhigh[:-1])
        d2 = (hlow[1:]>hlow[:-1])
        
        d_f = (d1.astype(int)+d2.astype(int))
        d_f[d_f == 2] = 4
        
        factor1 = rolling_norm(d_f, 242*5)[-60:]
    
        factor = np.nansum(factor1*mask, axis = 1)
        
        factor = np.nanmean(factor)
    
        return factor


   
class hhll_t3_CC_CFG_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'turnover_rate', 'low', 'high']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        
        tover = data['turnover_rate'].iloc[-135:]
        close_mask = data['close_preadj'].iloc[-95:]
        temp = bk.move_mean(tover, 60, min_count = 15, axis = 0)
        turnover = pd.DataFrame(temp,index = tover.index, columns = tover.columns).iloc[-60:]
        ret = (close_mask/close_mask.shift(30)-1).iloc[-60:]
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)
        temp6 = ret.gt(pd.Series(ret.quantile(0.80, axis = 1)), axis=0)
        mask = temp4*temp6
        
        hhigh = data['high_preadj'].iloc[-65:].values
        hlow = data['low_preadj'].iloc[-65:].values
        
        d1 = (hhigh[1:]>hhigh[:-1])
        d2 = (hlow[1:]>hlow[:-1])
        
        d_f = (d1.astype(int)+d2.astype(int))
        d_f[d_f == 2] = 4
        
        factor1 = d_f[-60:]

        factor = np.nansum(factor1*mask, axis = 1)
        
        factor = np.nanmean(factor)

        return factor
    
class td_cv_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'stk_index_corr_hs300', 'low', 'high']
    normalize_size = 720 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        stk_close = data['close_preadj'].iloc[-50:]
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = ts_std(stk_ret, 30).iloc[-15:]
        stk_index_corr = data['stk_index_corr_hs300'].iloc[-15:]
        temp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0)
        temp2 = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.80, axis = 1)), axis=0) 
        mask = temp2 * temp3

        hhigh = data['high_preadj'].iloc[-77:].values
        hlow = data['low_preadj'].iloc[-77:].values
        
        temp = bk.move_min(hlow, 10, min_count = 5, axis = 0)-bk.move_min(hlow, 60, min_count = 5, axis = 0)+bk.move_max(hhigh, 10, min_count = 5, axis = 0)-bk.move_max(hhigh, 60, min_count = 5, axis = 0)
        temp = temp[-15:]
        tempdf = np.nanmean(temp*mask, axis = 1)
        factor = np.nanmean(tempdf)
        
        return factor

class high_low_diff_stk2idx_zsj_if(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close','open', 'low', 'high', 'amount']
    normalize_size = 3000 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        #stk_close = data['close_preadj'].iloc[-75:].values
        stk_high = data['high_preadj'].iloc[-75:].values
        stk_low = data['low_preadj'].iloc[-75:].values
        stk_open = data['open_preadj'].iloc[-75:].values
        #stk_amount = data['amount_preadj'].iloc[-75:].values
        
        roll_win = 45
        #ma_win = 15
        #ts_pct_win = 3000
        #min_pct = 0.9
        min_periods = int(0.5 * roll_win)
        high_open_diff = stk_high - stk_open
        open_low_diff = stk_open - stk_low

        high_low_diff_stk = bk.move_sum(high_open_diff, roll_win, min_count = min_periods, axis = 0) - bk.move_sum(open_low_diff, roll_win, min_count = min_periods, axis = 0)
        high_low_diff_stk2idx_raw = np.nanmean(high_low_diff_stk, axis = 1)
        #factor = calc_ma_helper(high_low_diff_stk2idx_raw, ma_win, ts_pct_win, min_pct)[-1]
        factor  = np.nanmean(high_low_diff_stk2idx_raw[-15:])
        return factor


class kpz_dpo_std_zsj_if(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low', 'open']} 
    #data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        
        hclose = data['close_preadj'].iloc[-100:]
        dpo_win = 45
        ma_win = 30
        #ts_pct_win = 1200
        
        def calc_dpo_sig(close, roll_win):
            dpo = close[int(roll_win / 2 + 1):] - REF(MA(close, roll_win), int(roll_win / 2 + 1))
            return dpo   
        
        dpo_raw = calc_dpo_sig(hclose, dpo_win)
        dpo_std_raw = np.nanstd(dpo_raw[-ma_win:])
        
        return dpo_std_raw


class kpz_ma_displaced_std_zsj_if(FutureFactor):

    data_type = 'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low', 'open']} 
    #data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 242*5
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        
        close = data['close_cont_IC'].iloc[-180:]

        ##### calc factor #####

        def calc_ma_displaced(close, short_win=10, long_win=20):
            ma_close = MA(close, long_win)
            ma_displaced = REF(ma_close, short_win)
            ma_diff = close[short_win:] - ma_displaced
            return ma_diff


        short_win = 10
        long_win = 90
        score_raw = calc_ma_displaced(close, short_win, long_win)
 
        #factor = calc_std_helper(score_raw, std_win, 242*5, norm = True)
        factor = np.nanstd(score_raw[-40:])
        return factor



class stk2idx_maxret_diff_chg_zsj_if(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'turnover_rate', 'low', 'high']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        stk_close = data['close_preadj'].iloc[-100:]
        stk_close[abs(stk_close) < 1e-8] = np.nan
        stk_ret = stk_close / stk_close.shift(1) - 1

        ret_win = 60
        stk_max_ret = multi_processing_joblib(df=stk_ret, func=get_top_mean, n_jobs=20, d=ret_win)

        # common code for maxret_diff
        ret_win_short = 5
        stk_ret_duration = stk_close/stk_close.shift(ret_win_short) - 1 
        stk_maxret_diff = stk_max_ret - (stk_ret_duration/ret_win_short)
        stk_maxret_diff[~np.isfinite(stk_maxret_diff)] = np.nan
        stk2idx_maxret_diff_raw = np.nanmean(stk_maxret_diff, axis = 1)

        # factor logic
        short_win = 10
        long_win = 35
        min_pct = 0.9
        #stk2idx_maxret_diff_chg = calc_change_helper(stk2idx_maxret_diff_raw,short_win,long_win,ts_pct_win)
        factor = np.nanmean(stk2idx_maxret_diff_raw[-short_win:]) - np.nanmean(stk2idx_maxret_diff_raw[-long_win:])
        
        return factor
    
    


    