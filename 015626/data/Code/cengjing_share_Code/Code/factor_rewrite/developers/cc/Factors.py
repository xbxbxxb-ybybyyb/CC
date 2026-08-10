# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 10:34:59 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd
from operators_cc import *


class CDO_CC(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['close', 'open']} 
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    num_range = '(-0.5, 1]'
                   
    def calculate(self, data):
        
        hclose = data['close_cont_IC'].values[-120:]
        hopen = data['open_cont_IC'].values[-120:]
        factor = np.nanmean(hclose)/np.nanmean(hopen)

        return factor

    
class CDO_ind_CC(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close', 'open']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        
        hclose = data['close_000905.SH'].values[-150:]
        hopen = data['open_000905.SH'].values[-150:]
        factor = np.nanmean(hclose)-np.nanmean(hopen)
        
        return factor



class CLP_CC(FutureFactor):

    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close','position']}  
    normalize_size = 1200
    normalize_type = 'rolling_norm'
    num_range = '[-0.3, 1]'
    
    def calculate(self, data):
        
        hclose = (data['close_cont_IC'].values)[-40:]
        position = (data['position_cont_IC'].values)[-40:]
        temp1 = (np.where(hclose>0, 1, np.where(hclose<0, -1, 0)))
        temp3 = position - shift(position, 1)
        temp2 = np.abs(temp3*temp1)
        
        factor = bk.move_mean(temp2, 30, min_count = 15)

        return factor[-1]



    
class ClMaxClMin_IFIC_CC(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['close']} 
    normalize_size = 3 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        hclose = data['close_cont_IF'].values[-30:]
        
        factor = np.nanmax(hclose)/np.nanmin(hclose)

        
        return factor


    
class ClMaxClMin_ind_CC(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']} 
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    num_range = '(-0.2, 1]'
    
    def calculate(self, data):
        
        hclose = data['close_000905.SH'].values[-40:]
        
        factor = np.nanmax(hclose)/np.nanmin(hclose)

        
        return factor



class CloseVoltoMean_IFIC_CC(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']} 
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    #num_range = [-0.2, 1]
    
    def calculate(self, data):
        
        hclose = (data['close_000300.SH'].values)[-39:]
        return np.nanmean(bk.move_std(hclose, 30, min_count = 10)/bk.move_mean(hclose, 30, min_count = 15))



class CloseVoltoMean_ind_CC(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']} 
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    num_range = '(-0.2, 1]'
    
    def calculate(self, data):
        
        hclose = (data['close_000905.SH'].values)[-40:]
        return np.nanstd(hclose)/np.nanmean(hclose)



class GA_ind_IFIC_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close', 'high', 'low', 'open']} 
    normalize_size = 5 * 240
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


class HcorrC_ind_IFIC_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['high','close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = [0.0001, 1]
    
    def calculate(self, data):

        high = data['high_cont_IF'].iloc[-60:]
        close = data['close_cont_IF'].iloc[-60:]
        factor = high.corr(close)
        return factor


class hhll_ind_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['high', 'low']}  
    normalize_size = 2420
    normalize_type = 'ts_rank'
    #num_range = [-0.499999, 1]
    
    def calculate(self, data):
       
        hhigh = data['high_000905.SH'].iloc[-60:]
        hlow = data['low_000905.SH'].iloc[-60:]
        temp = np.where((hhigh>hhigh.shift(1)) & (hlow>hlow.shift(1)), 4, np.where((hhigh<hhigh.shift(1)) & (hlow<hlow.shift(1)), 0, 1))
        
        return np.nanmean(temp[-45:])


class HcorrC_ind_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':[ 'high', 'close']}
    normalize_size = 2420
    normalize_type = 'ts_rank'
    #num_range = [0.0001, 1]
    
    def calculate(self, data):

        high = data['high_000905.SH'].iloc[-60:]
        close = data['close_000905.SH'].iloc[-60:]
        factor = high.corr(close)
        return factor
    

class HHLS_ind_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['high']}  
    normalize_size = 1200
    normalize_type = 'rolling_norm'
    #num_range = [-0.3, 1]
    
    def calculate(self, data):
        
        hhigh = (data['high_000905.SH'].values)[-120:]
        factor = np.nanmax(hhigh[-50:]) - np.nanmax(shift(hhigh, 50)[-50:])

        return factor[-1]    



class HL123_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['high','low']} 
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = '[0, 1]'
    
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



class HLLSVol_CC(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['high','low']} 
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = '[0, 1]'
    
    def calculate(self, data):
        hlow = (data['low_cont_IC'].values)[-250:]
        hhigh = (data['high_cont_IC'].values)[-250:]
        a = bk.move_std(hhigh/hlow, 240, min_count = 10)
        a[a<1e-10] = np.nan
        factor = bk.move_std(hhigh/hlow, 40, min_count = 10)/a
        return factor[-1]




class HLTM_IFIC_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['high','low', 'vwap']} 
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = [0, 1]
    
    def calculate(self, data):
        hlow = (data['low_cont_IF'].values)[-60:]
        hhigh = (data['high_cont_IF'].values)[-60:]
        vwap =(data['vwap_cont_IF'].values)[-60:]
        temp1 = bk.move_max(hhigh, 15, min_count = 7) - vwap
        temp2 = vwap - bk.move_min(hlow, 15, min_count = 7)
        temp = np.where(temp1>temp2, temp1, temp2)
        factor = bk.move_mean(temp, 40, min_count = 15)
        return factor[-1]



class HLTM_ind_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 6
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['high', 'low', 'close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = [0, 1]
    
    def calculate(self, data):
        hlow = (data['low_000905.SH'].values)[-1100:]
        hhigh = (data['high_000905.SH'].values)[-1100:]
        hclose =(data['close_000905.SH'].values)[-1100:]
        temp1 = bk.move_max(hhigh, 15, min_count = 7) - hclose
        temp2 = hclose - bk.move_min(hlow, 15, min_count = 7)
        temp = np.where(temp1>temp2, temp1, temp2)
        factor0 = bk.move_mean(temp, 30, min_count = 15)
        factor = rolling_norm(factor0, 242*4)
        return factor[-1]
    
    
class HmaxC_ind_CC(FutureFactor):
  
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['high', 'low', 'close']}
    normalize_size = 1000
    normalize_type = 'ts_rank'
    num_range = '[0, 1]'
    
    def calculate(self, data):

        hhigh = (data['high_000905.SH'].values)[-130:]
        hclose =(data['close_000905.SH'].values)[-130:]
        temp1 = -bk.move_max(hhigh, 120, min_count = 90) / hclose
        temp1[abs(temp1)>100000] = np.nan
        
        return temp1[-1]    



class IFIC4_CC(FutureFactor):
  
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':[ 'close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = [0, 1]
    
    def calculate(self, data):

        hclose = (data['close_000300.SH'].values)[-65:]
        temp1 = bk.move_mean(hclose, 60, min_count = 15) - bk.move_mean(shift(hclose, 20), 40, min_count =7)
        factor = np.abs(temp1)
        
        return factor[-1]



class L123_CC(FutureFactor):

    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['low']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = '[0, 1]'
    
    def calculate(self, data):

        hlow = (data['low_cont_IC'].values)[-90:]
        i11 = bk.move_min(hlow, 10, min_count = 5) - bk.move_min(hlow, 25, min_count = 10)
        i12 = bk.move_min(hlow, 20, min_count = 15) - bk.move_min(hlow, 30, min_count = 10)
        i2 = bk.move_mean((i11-i12), 30, min_count = 2)

        
        return i2[-1]

class L123_ind_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':[ 'low']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = [0.0001, 1]
    
    def calculate(self, data):

        hlow = (data['low_000905.SH'].values)[-80:]
        i11 = bk.move_min(hlow, 10, min_count = 5) - bk.move_min(hlow, 25, min_count = 10)
        i12 = bk.move_min(hlow, 20, min_count = 15) - bk.move_min(hlow, 30, min_count = 10)
        i2 = bk.move_mean((i11-i12), 25, min_count = 2)

        
        return i2[-1]


class LCCorr_ind_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':[ 'low', 'close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = [0.0001, 1]
    
    def calculate(self, data):

        high = data['low_000905.SH'].iloc[-60:]
        close = data['close_000905.SH'].iloc[-60:]
        factor = high.corr(close)
        return factor
    

class LCCorr_ind_IFIC_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':[ 'low', 'close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = [0.0001, 1]
    
    def calculate(self, data):

        high = data['low_000300.SH'].iloc[-60:]
        close = data['close_000300.SH'].iloc[-60:]
        factor = high.corr(close)
        return factor
    

class LSC_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 5
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['high','close', 'low']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = '[0, 1]'
    
    def calculate(self, data):

        high = (data['high_cont_IC'].values)[-1100:]
        close = (data['close_cont_IC'].values)[-1100:]
        low = (data['low_cont_IC'].values)[-1100:]
        temp = (bk.move_max(high, 30, min_count = 10)- bk.move_min(low, 30, min_count = 10))
        temp[abs(temp)<0.0001] = np.nan
        hh = (bk.move_max(high, 30, min_count = 10) - close)/temp
        ll = (close -bk.move_min(low, 30, min_count = 10))/temp
        factor = bk.move_mean(ll, 20, min_count =15) - bk.move_mean(hh, 20, min_count =15)
        factor = rolling_norm(factor, 242*4)
        factor[factor<=-0.5] = np.nan
        factor = bk.move_mean(factor, 3, min_count = 2)
        return factor[-1]
    

class LminLmean_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':[ 'low']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = '(-0.5, 1]'
    
    def calculate(self, data):


        low = data['low_cont_IC'].values[-60:]
        temp1 = np.nanmin(low)
        temp2 = np.nanmean(low[-30:])
        factor = -temp1/temp2
        return factor
    

class LminLmean_IFIC_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':[ 'low']}
    normalize_size = 242*3
    normalize_type = 'ts_rank'
    #num_range = [-0.499999, 1]
    
    def calculate(self, data):


        low = data['low_cont_IF'].values[-60:]
        temp1 = np.nanmin(low)
        temp2 = np.nanmean(low[-30:])
        factor = -temp1/temp2
        return factor
    

class LminLmean_ind_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':[ 'low']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = [-0.499999, 1]
    
    def calculate(self, data):


        low = data['low_000905.SH'].values[-50:]
        temp1 = np.nanmin(low)
        temp2 = np.nanmean(low[-30:])
        factor = -temp1/temp2
        return factor
    

class MALS_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 11
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':[ 'close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = [0, 1]
    
    def calculate(self, data):

        hclose = (data['close_cont_IC'].values)[-2500:]
        shift_20 = shift(hclose, 20)
        shift_20[shift_20==0] = np.nan
        temp = bk.move_mean(hclose, 60, min_count = 15) -  bk.move_mean(shift_20, 40, min_count = 7)
        factor = bk.move_mean(temp, 3, min_count = 1)
        factor = np.abs(factor)
        factor = rolling_norm(factor, 2420)
        return factor[-1]

class OCtHL_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':[ 'close','low','high', 'open']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = [-0.499999, 1]
    
    def calculate(self, data):

        hopen = (data['open_cont_IC'].values)[-40:]
        hclose = (data['close_cont_IC'].values)[-40:]
        hhigh = (data['high_cont_IC'].values)[-40:]
        hlow = (data['low_cont_IC'].values[-40:])
        temp1 = hopen - hclose
        temp2 = hhigh - hlow
        temp2[abs(temp2)<1e-8] = np.nan
        
        t_pcor2 = -temp1/temp2
        
        t_pcor2[abs(t_pcor2) > 1e8] = 0
        
        factor = bk.move_mean(bk.move_mean(t_pcor2, 30, min_count = 15),5, min_count = 2) 
        
        return factor[-1]



class OCtHL_ind_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close','low','high', 'open']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = [-0.499999, 1]
    
    def calculate(self, data):

        hopen = (data['open_000905.SH'].values)[-40:]
        hclose = (data['close_000905.SH'].values)[-40:]
        hhigh = (data['high_000905.SH'].values)[-40:]
        hlow = (data['low_000905.SH'].values[-40:])
        temp1 = hopen - hclose
        temp2 = hhigh - hlow
        temp2[abs(temp2)<1e-8] = np.nan
        
        t_pcor2 = -temp1/temp2
        
        t_pcor2[abs(t_pcor2) > 1e8] = 0
        
        factor = bk.move_mean(bk.move_mean(t_pcor2, 30, min_count = 15),5, min_count = 2) 
        
        return factor[-1]
    


class PositiontoVolume2_IFIC_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':[ 'position', 'volume']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = [-0.499999, 1]
    
    def calculate(self, data):

        a = (data['position_cont_IF'].values)[-20:]
        a[abs(a) < 1e-8] = np.nan
        hvolume = (data['volume_cont_IF'].values[-20:])
        temp = hvolume/a
        factor = np.nanmean(temp)
        return factor
    

class Rev_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 11
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':[ 'close']}
    normalize_size = 2420
    normalize_type = 'rolling_norm'
    num_range = '[-0.5, 1]'
    
    def calculate(self, data):
        hclose = data['close_cont_IC'].iloc[-190:]
        ret = (hclose/hclose.shift(180)-1).values
        #print(shift(hclose, 180))
        factor = bk.move_mean(ret, 3, min_count = 2)
        #print(factor[-1])
        return factor[-1]
    


class Rev_ind_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 21
    data_dict = dict()
    data_dict['Index_Id'] = {'IC':[ 'close']}
    normalize_size = 4800
    normalize_type = 'rolling_norm'
    num_range = '[-1, 1]'
    
    def calculate(self, data):
        hclose = data['close_000905.SH'].iloc[-150:]
        ret = (hclose/hclose.shift(120)-1).values

        return ret[-1]
    


class RolTrendLS_ind_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 21
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':[ 'high', 'low', 'close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = [-1, 1]
    
    def calculate(self, data):
        hclose = (data['close_000905.SH'].values)[-85:]
        hhigh = (data['high_000905.SH'].values)[-85:]
        hlow = (data['low_000905.SH'].values)[-85:]
        a = bk.move_max(hhigh, 60, min_count = 15) - bk.move_min(hlow, 60, min_count = 15)
        a[abs(a)<1e-8] = np.nan
        ll = (hclose - bk.move_min(hlow, 60, min_count = 15))/a
        a2 = bk.move_mean(ll, 10, min_count = 5)
        a3 = bk.move_mean(a2, 10, min_count = 5)
        vwtc_r = 3*a3-2*a2
        return vwtc_r[-1]
    

class SYXWR_ind_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':[ 'high', 'low', 'close', 'open']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = [-1, 1]
    
    def calculate(self, data):
        hopen = (data['open_000905.SH'].values)[-120:]
        hhigh = (data['high_000905.SH'].values)[-120:]
        hlow = (data['low_000905.SH'].values)[-120:]
        hclose = (data['close_000905.SH'].values)[-120:]
        
        temp1 = np.where(hopen>hclose, hopen, hclose)
        #temp2 = np.where(hopen>hclose, hclose, hopen)
        
        b = bk.move_mean((hhigh - temp1), 30, min_count = 15)
        b[abs(b)<1e-8] = np.nan
        t_pcor = (hhigh-temp1)/b
        a = bk.move_max(hhigh, 30, min_count = 15) - bk.move_min(hlow, 30, min_count = 15)
        a[abs(a) < 1e-8] = np.nan
        t_pcor2 = (hclose-bk.move_min(hlow, 30, min_count = 15))/a

        
        return np.nanmean((t_pcor2 - t_pcor)[-90])


class SmaxSmean_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['share']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        hshare = (data['share_cont_IC'].values)[-120:]
        
        a = np.nanmean(hshare[-30:])
        b = np.nanmean(hshare)
        factor = a-b
        return factor


class ZHZH_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['high']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        hhigh = (data['high_cont_IC'].values)[-110:]
        factor = bk.move_mean((hhigh>=bk.move_max(hhigh, 10, min_count = 5)).astype(int), 90, min_count = 5)
        
        return factor[-1]

class ZHZH_ind_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['high']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = '[0, 1]'
    
    def calculate(self, data):
        hhigh = (data['high_000905.SH'].values)[-80:]
        factor = bk.move_mean((hhigh>=bk.move_max(hhigh, 15, min_count = 5)).astype(int), 60, min_count = 5)
        
        return factor[-1]


class fvs2_ind_IFIC_CC(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    data_dict['Continuous_Data'] = {'IF':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
   # num_range = [0, 1]
    
    def calculate(self, data):
        close_spot = (data['close_000300.SH']).iloc[-52:]
        close = (data['close_cont_IF']).iloc[-52:]
        vwtc_r = close.rolling(40, min_periods=15).corr(close_spot)
        vwtc_r  = vwtc_r.replace([-np.inf, np.inf], np.nan)
        vwtc_r = vwtc_r.values
        factor = (vwtc_r*(np.sign(-(close-close_spot))))
        factor = np.abs(factor)
        factor = bk.move_mean(factor, 5, min_count = 2)
        
        return factor[-1]
    
    

class td_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Index_Id'] = {'000300.SH':['close']}
    data_dict['Continuous_Data'] = {'IC':['low', 'high']}
    normalize_size = 1200
    normalize_type = 'rolling_norm'
    num_range = '[-0.5, 1]'
    
    def calculate(self, data):
        hlow = (data['low_cont_IC'].values)[-60:]
        hhigh = (data['high_cont_IC'].values)[-60:]
        templ = np.nanmin(hlow[-10:]) - np.nanmin(hlow)
        temph = np.nanmax(hhigh[-10:]) - np.nanmax(hhigh)
        factor = templ+temph
        return factor
    

class vc_ind_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['volume', 'close']}
    #data_dict['Continuous_Data'] = {'IC':['low', 'high']}
    normalize_size = 1200
    normalize_type = 'rolling_norm'
    num_range = '[-1, 1]'
    
    def calculate(self, data):
        hvolume = (data['volume_000905.SH'].values)[-20:]
        hclose = (data['close_000905.SH'].values)[-20:]
        factor = bk.move_mean((hvolume-shift(hvolume, 1)), 15, min_count = 7)*(hclose - shift(hclose, 15))
        return -factor[-1]
    

########################## CFGs ##############################


    
class BS_Main_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['amount','BuyUniqueOrderNum','BuyTradeNum', 'SellUniqueOrderNum', 'SellTradeNum']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        amount = data['amount'].iloc[-25:]
        df_s = amount.rolling(10, min_periods = 5).sum()
        
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0).astype(float).values
        bool_df[bool_df==0] = np.nan
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-25:]
        BuyTradeNum = data['BuyTradeNum'].values[-25:]
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-25:]
        SellTradeNum = data['SellTradeNum'].values[-25:]
        
        factor = BuyUniqueOrderNum/BuyTradeNum - SellUniqueOrderNum/SellTradeNum


        factor = np.nanmean(np.nanmean(factor * bool_df, axis = 1)[-6:])

        return -factor

class BS4_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['Bid1AmtMean', 'BuyNumOrdersSumMean', 'weight']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        Bid1AmtMean = data['Bid1AmtMean'].values[-10:]
        BuyNumOrdersSumMean = data['BuyNumOrdersSumMean'].values[-10:]
        weight = data['weight'].values[-1]
        temp1 = (Bid1AmtMean/BuyNumOrdersSumMean)
        temp1 = np.nanmean(temp1, axis = 0)
        temp1[abs(temp1)>10000] = np.nan
        temp = (temp1*weight)
        return np.nanmean(temp)


class BS_7_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_superorder_money', 'buy_bigorder_money', 'amount']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        amount = data['amount'].iloc[-65:]
        df_s = amount.rolling(60, min_periods = 5).sum()
        bool_df = (df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)).values.astype(float)
        bool_df[bool_df==0] = np.nan
        
        buy_superorder_money_500 = data['buy_superorder_money'].fillna(0).values[-65:]
        buy_bigorder_money_500 = data['buy_bigorder_money'].fillna(0).values[-65:]
        amount = data['amount'].values[-65:]
        factor = (buy_superorder_money_500+buy_bigorder_money_500)/amount
        
        factor[abs(factor)>100000] = np.nan

        factor = np.nanmean(factor[-15:], axis = 0)
        factor = np.nanmean(factor*bool_df[-1])
            
        return np.nanmean(factor)


class CFG12_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'low', 'weight', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        hclose = data['close_preadj'].values[-125:]
        hlow = data['low_preadj'].values[-125:]
        weight = data['weight'].values[-125:]
        g = bk.move_min(hlow, 120, min_count = 90, axis = 0)/hclose
        g1 = np.nanmean((g*weight)[-1])
        gg1 = (-g1)
        return gg1
    

class CFG18_CC(FutureFactor):
    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['high','close','weight','adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '(-0.5, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):

        hclose = data['close_preadj'].iloc[-48:]
        hweight = data['weight'].iloc[-48:]

        
        hret = hclose/hclose.shift(1)-1
        htemp = (hret*hweight).mean(axis = 1)
        htemp = bk.move_mean(htemp, 45, min_count = 15, axis = 0)
        #htemp = bk.move_mean((hhigh>bk.move_max(hhigh, 45, min_count = 5, axis = 0)), 90, min_count = 5, axis = 0)
        factor = htemp[-1]        
        return factor


class CFG1_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['amount','close','weight', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        amount = data['amount'].iloc[-156:]
        df_s = amount.rolling(120, min_periods = 5).sum()
        bool_df = (df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)).values
        hclose = data['close_preadj'].values[-38:]
        weight = data['weight'].values[-38:]

        hret = (hclose[1:]/hclose[:-1]-1)
        temp_weighted = hret[-36:]*weight[-36:]*bool_df[-36:]
        a = bk.move_mean(np.nanmean(temp_weighted, axis = 1), 35, min_count = 15)
        return a[-1]


class CFG20_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 10
    data_dict = dict()
    data_dict['Stock'] = ['high','low','close','weight', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '[0, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        hlow = data['low_preadj'].values[-1000:]
        hhigh = data['high_preadj'].values[-1000:]
        hclose = data['close_preadj'].values[-1000:]
        hweight = data['weight'].values[-1000:]
        
        h = bk.move_max(hhigh, 90, min_count = 10, axis = 0)
        l = bk.move_min(hlow, 90, min_count = 10, axis = 0)
        
        r =  h - l
        r[abs(r)<1e-8] = np.nan
        
        hh = (h - hclose)/r 

        ll = (hclose - l)/r
        vwtc_r = bk.move_mean(ll, 20, min_count = 5, axis = 0)
        vw = bk.move_mean(hh, 20, min_count = 5, axis = 0)
        
        a = vwtc_r-vw
        
        htemp = np.nanmean((a*hweight), axis = 1)
        htemp = rolling_norm(htemp, 242*3)
        htemp[abs(htemp)>1] = 0
        htemp = np.nanmean(htemp[-3:])
        return htemp


class CFG21_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 10
    data_dict = dict()
    data_dict['Stock'] = ['high','low','close','weight', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        hlow = data['low_preadj'].values[-61:]
        hweight = data['weight'].values[-61:]
        
        a = -bk.move_min(hlow, 60, min_count =15, axis = 0)/bk.move_mean(hlow, 15, min_count =5, axis = 0)
        htemp = np.nanmean(a*hweight, axis = 1)[-1]
        return htemp 



class CFG23_2_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 10
    data_dict = dict()
    data_dict['Stock'] = ['close', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '[-0.5, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        amount = data['amount'].iloc[-121:]
        close = data['close_preadj'].iloc[-46:]
        df_s = amount.rolling(120, min_periods = 5).sum()
        bool_df = (df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)).values[-46:].astype(float)
        bool_df[bool_df==0] = np.nan
        x = np.array(range(len(close)))
        holder = {}
        for item in close.columns:
            close_spot = close[item].values
            holder[item] = pd.Series(rolling_linear_reg(x, close_spot, 45))
        temp1 = pd.DataFrame(holder)
        temp1.index = close.index
        temp = (temp1*bool_df).mean(axis = 1)
        
        return temp.iloc[-1]
    


class CFG23_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 10
    data_dict = dict()
    data_dict['Stock'] = ['close', 'adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '[0, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        index_close = data['close_000905.SH'].iloc[-1203:]
        stk_close = data['close_preadj'].iloc[-1203:]
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.iloc[-1200:].corrwith(index_ret.iloc[-1200:, 0])
        #stk_index_corr = ((stk_ret.iloc[-1201:]).rolling(1200, min_periods=600).corr(index_ret.iloc[-1201:, 0])).iloc[0]
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        bool_df = stk_index_corr.gt(stk_index_corr.quantile(0.90)).astype(float)
        #bool_df = (stk_index_corr.argsort().argsort()>=(np.shape(stk_index_corr)[-1]*0.9))
        temp = pd.Series(np.array(range(len(bool_df))))
        temp.index =  bool_df.index
        temp.name =  bool_df.name

        stk_close = stk_close.iloc[-61:]
        x = np.array(range(len(stk_close)))
        holder = {}
        for item in stk_close.columns:
            close_spot = stk_close[item].values
            holder[item] = pd.Series(rolling_linear_reg(x, close_spot, 60))
        temp1 = pd.DataFrame(holder)
        temp1.index = stk_close.index
        #print(bool_df.sum())
        temp = ((temp1.iloc[-1])*bool_df).mean()
        
        return temp


class CFG26_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 10
    data_dict = dict()
    data_dict['Stock'] = ['close','adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 242*3 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '[-0.5, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        amount = data['amount'].iloc[-120:]
        df_s = amount.sum(axis = 0)
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90)).iloc[0])
        
        index_close = data['close_000905.SH'].iloc[-1203:]
        stk_close = data['close_preadj'].iloc[-1203:]
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.iloc[-1200:].corrwith(index_ret.iloc[-1200:, 0])
        #stk_index_corr = ((stk_ret.iloc[-1201:]).rolling(1200, min_periods=600).corr(index_ret.iloc[-1201:, 0])).iloc[0]
        bool_df = stk_index_corr[stk_amount]
        
        hclose =  stk_close.iloc[-60:]
        hmhm_r = hclose.mean(axis = 0) - hclose.shift(20).mean(axis = 0)
        factor = (hmhm_r*bool_df).mean()
        return factor

class CFG7_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['turnover_rate', 'close', 'open', 'adjfactor']
    #data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        to = data['turnover_rate'].iloc[-120:]
        hclose = data['close_preadj'].iloc[-120:]
        
        hopen = data['open_preadj'].iloc[-120:]
        ret = hclose/hopen -1
        hret = hclose/hclose.shift(1) -1
        cc1 = ((to[hclose<hopen]/abs(ret[hclose<hopen])))
        #ccc1 = cc1.rolling(60, min_periods = 7).mean()
        ccc1 = pd.DataFrame(bk.move_mean(cc1, 60, min_count = 7, axis = 0), index = cc1.index, columns = cc1.columns)
        cc2 = to_ts(ccc1, hret)
        ccc2 = np.nanmean(cc2.iloc[-60:])
        return ccc2

class CFG8_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 10
    data_dict = dict()
    data_dict['Stock'] = ['float_shares', 'volume', 'close', 'adjfactor']
    #data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '(-0.5, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        hvolume = data['volume_preadj'].iloc[-31:]
        hclose = data['close_preadj'].iloc[-31:]
        hfs = data['float_shares'].iloc[-31:]
        hret = hclose/hclose.shift(1) - 1
        d1 = hvolume/hclose/hfs
        d1 = to_ts(d1, hret)
        dd1 = np.nanmean(d1.iloc[-30:])
        return dd1

class CFG9_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [ 'volume', 'close', 'adjfactor']
    #data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '(0, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):

        hclose = data['close_preadj'].iloc[-61:]
        hret = hclose/hclose.shift(1) - 1
        hmax = pd.DataFrame(bk.move_max(hclose, 30, min_count = 20, axis =0), index = hclose.index, columns = hclose.columns)
        hmin = pd.DataFrame(bk.move_min(hclose, 30, min_count = 20, axis =0), index = hclose.index, columns = hclose.columns)
        e = hmax/hmin
        e1 = to_ts(e, hret)
        
        dd1 = np.nanmean(e1.iloc[-30:])
        return dd1


class CloseVoltoMean_cr_CFG_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 10
    data_dict = dict()
    data_dict['Stock'] = [ 'volume', 'close', 'adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 720 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):

        index_close = data['close_000905.SH'].iloc[-1225:]
        stk_close = data['close_preadj'].iloc[-1225:]
        stk_ret = stk_close.pct_change(1, fill_method=None)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = (stk_ret.rolling(1200, min_periods=1200).corr(index_ret.iloc[:,0])).iloc[-61:]
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        
        mask = (2 * stk_index_corr.rank(axis=1, pct=True) - 1).values
        
        stk_close = stk_close.iloc[-61:]
        
        prstd3_r = bk.move_std(stk_close, 40, min_count = 5, axis = 0)/bk.move_mean(stk_close, 40, min_count = 5, axis = 0)
        
        factor = np.nansum((prstd3_r*mask), axis = 1)
        factor = np.nanmean(factor[-20:])

        return factor


class CrossingTurns_CFG_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 10
    data_dict = dict()
    data_dict['Stock'] = [ 'amount', 'close', 'open', 'adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '(-0.5, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):

        amount = data['amount'].iloc[-120:]
        df_s = amount.sum(axis = 0)
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90)).iloc[0])
        
        index_close = data['close_000905.SH'].iloc[-1203:]
        stk_close = data['close_preadj'].iloc[-1203:]
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.iloc[-1200:].corrwith(index_ret.iloc[-1200:, 0])
        stk_index_corr = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90)).iloc[0])
        bool_df = (stk_index_corr*stk_amount).values.astype(float)
        bool_df[bool_df==0] = np.nan
        
        hclose = data['close_preadj'].values[-45:]
        hopen = data['open_preadj'].values[-45:]
        
        hhigh = data['high_preadj'].values[-45:]
        hlow = data['low_preadj'].values[-45:]
        
        temp = np.abs(hclose-hopen)
        temp[temp==0] = 0.01
        #temp.index = hclose.index
        temp0 = (hhigh - hlow)
        temp1 = (temp0/temp)[-15:]
        a = (bk.move_sum((hclose[1:]/hclose[:-1]-1), 30, min_count = 15, axis = 0))[-15:]
        vwtc_r = np.nanmean((temp1*(a)), axis = 0)

        factor = np.nanmean(vwtc_r*bool_df)
        
        return factor


class DJC_cv_CFG_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 10
    data_dict = dict()
    data_dict['Stock'] = [  'close', 'adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):

        index_close = data['close_000905.SH'].iloc[-1206:]
        stk_close = data['close_preadj'].iloc[-1206:]
        stk_ret = stk_close.pct_change(1, fill_method=None)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = (stk_ret.rolling(1200, min_periods=1200).corr(index_ret.iloc[:,0])).iloc[-5:]
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        
        stk_volatility = ts_std(stk_ret.iloc[-37:], 30).iloc[-5:]
        tempp2 = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.80, axis = 1)), axis=0)
        tempp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0)
        
        hclose = stk_close.iloc[-220:]
        temp5 = bk.move_mean(hclose.iloc[-40:], 5, min_count = 2, axis = 0)
        temp10 = bk.move_mean(hclose.iloc[-40:], 10, min_count = 5, axis = 0)
        temp20 = bk.move_mean(hclose.iloc[-55:], 20, min_count = 10, axis = 0)
        temp60 = bk.move_mean(hclose.iloc[-105:], 60, min_count = 20, axis = 0)
        temp120 = bk.move_mean(hclose.iloc[-205:], 120, min_count = 60, axis = 0)
        
        temp5_diff = ((temp5[1:]-temp5[:-1]>0).astype(int))[-26:]
        temp10_diff = ((temp10[1:]-temp10[:-1]>0).astype(int))[-26:]
        temp20_diff = ((temp20[1:]-temp20[:-1]>0).astype(int))[-26:]
        temp60_diff = ((temp60[1:]-temp60[:-1]>0).astype(int))[-26:]
        temp120_diff = ((temp120[1:]-temp120[:-1]>0).astype(int))[-26:]
        
        temp = (bk.move_mean((temp5_diff+temp10_diff+temp20_diff+temp60_diff+temp120_diff), 20, min_count = 15, axis = 0))[-5:]
        mask = (tempp2 * tempp3).values
        factor = np.nansum((temp*mask), axis = 1)
        factor = np.nanmean(factor)
        
        return factor


class GA_CFG_CC(FutureFactor):
  
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [ 'amount', 'close','low','high', 'open', 'adjfactor']
    #data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):

        amount = data['amount'].iloc[-120:]
        df_s = amount.sum(axis = 0)
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90)).iloc[0]).values.astype(float)
        bool_df[bool_df==0] = np.nan
        
        hhigh = data['high_preadj'].values[-120:]
        hclose = data['close_preadj'].values[-120:]
        hlow = data['low_preadj'].values[-120:]
        o= data['open_preadj'].iloc[-125:].shift(120).values[-1]
        h = np.nanmax(hhigh, axis = 0)
        l = np.nanmin(hlow, axis = 0)
        
        a = h-o
        b = hclose - l 
        c = (h-l)*2
        c[abs(c) < 1e-8] = np.nan
        vwtc_r = ((a+b)/c)[-1]
        factor = np.nanmean(vwtc_r*bool_df)
        return factor


class GA_ind_nr_w_a_CFG_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = [ 'amount', 'weight', 'close','low','high', 'open', 'adjfactor']
    #data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 242 # normalize所用历史数据长度
    normalize_type = 'roling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):

        amount = data['amount'].iloc[-120:]
        df_s = amount.sum(axis = 0)
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80)).iloc[0]).values
        stk_weight = data['weight'].iloc[-1].values
        bool_df = (stk_weight*temp1)
        
        hhigh = data['high_preadj'].values[-370:]
        hclose = data['close_preadj'].values[-370:]
        hlow = data['low_preadj'].values[-370:]
        o= data['open_preadj'].iloc[-370:].shift(120).values
        h = bk.move_max(hhigh, 120, min_count = 60, axis = 0)
        l = bk.move_min(hlow, 120, min_count = 60, axis = 0)
        
        a = h-o
        b = hclose - l 
        c = (h-l)*2
        c[abs(c) < 1e-8] = np.nan
        vwtc_r = ((a+b)/c)
        vwtc_r = rolling_norm(vwtc_r, 242)[-1]
        factor = np.nanmean(vwtc_r*bool_df)
        return factor
    
################################################################################################    
class HDLD_CFG2_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 10
    data_dict = dict()
    data_dict['Stock'] = [ 'amount', 'weight', 'close','low','high', 'open', 'adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '(-0.5, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):

        index_close = data['close_000905.SH'].iloc[-1945:]
        stk_close = data['close_preadj'].iloc[-1945:]
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = (stk_ret.rolling(1200, min_periods=1200).corr(index_ret.iloc[:,0])).iloc[-750:]
        
        stk_index_corr = (stk_index_corr.replace([-np.inf, np.inf], np.nan))
        bool_df = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0).values.astype(float)
        
        hclose = data['close_preadj'].iloc[-755:].values
        hopen = data['open_preadj'].iloc[-755:].values
        
        hlow = data['low_preadj'].iloc[-755:].values
        hhigh = data['high_preadj'].iloc[-755:].values
        
        temp = np.abs(hclose-hopen)
        temp[temp==0] = 0.01
        
        temp0 = (hhigh - hlow)
        temp1 = (temp0/temp)[-750:]
        a = bk.move_sum((hclose[1:]/hclose[:-1]-1), 30, min_count = 15, axis = 0)[-750:]
        vwtc_r = (temp1*(a))#.rolling(20, min_periods = 2).mean()
        
        bool_df[bool_df==0] = np.nan
        factor = np.nanmean(vwtc_r*bool_df, axis = 1)
        
        factor = bk.move_mean(factor,10,  min_count = 5, axis = 0)
        #print(b.iloc[:, 0].corr(b1.iloc[:, 0]))
        factor2 = rolling_norm(factor, 242*3, method = 'ts_rank')
        factor2 = np.nanmean(factor2[-3:])

        return factor2
##################################################################################################


class HDLD_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'low', 'weight', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        amount = data['amount'].iloc[-120:]
        df_s = amount.sum(axis = 0)
        bool_df = df_s.gt((df_s.quantile(0.90))).values.astype(float)
        bool_df[bool_df==0] = np.nan
        hopen = data['open_preadj'].iloc[-65:].values
        hclose = data['close_preadj'].iloc[-65:].values
        temp1 = np.where(hopen>hclose, hopen, hclose)
        temp2 = np.where(hopen>hclose, hclose, hopen)
        
        t_pcorr = np.nanmean(((temp1[1:] - temp1[:-1])+(temp2[1:] - temp2[:-1]))[-60:], axis = 0)
        
        factor = np.nanmean(t_pcorr*bool_df)

        return factor


class HHLS_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['amount','high', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        amount = data['amount'].iloc[-120:]
        df_s = amount.sum(axis = 0)
        bool_df = df_s.gt((df_s.quantile(0.90))).values.astype(float)
        bool_df[bool_df==0] = np.nan
        hhigh = data['high_preadj'].iloc[90:]
        hhigh_s = hhigh.shift(40).values
        hhigh = hhigh.values
        hdl_r = bk.move_max(hhigh, 40, min_count = 15, axis = 0) - bk.move_max(hhigh_s, 40, min_count = 15, axis = 0)
        hdl_r = np.nanmean(hdl_r[-10:], axis = 0)
        factor = np.nanmean(hdl_r*bool_df)
        return factor


class HL123_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['amount','high', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '(-0.5, 1]'# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        hlow = data['low_preadj'].iloc[-100:]
        hhigh = data['high_preadj'].iloc[-100:]
        hhigh_s = hhigh.shift(30).values
        hlow_s = hlow.shift(30).values
        
        hlow = hlow.iloc[-66:].values
        hhigh = hhigh.iloc[-66:].values
        
        i11 = (bk.move_max(hhigh, 10, min_count = 5, axis = 0)-bk.move_min(hlow, 60, min_count = 10, axis = 0))[-5:]
        i12 = (bk.move_max(hhigh_s, 10, min_count = 5, axis = 0)-bk.move_min(hlow_s, 60, min_count = 10, axis = 0))[-5:]
        i2 = np.nanmean((i11-i12))
        
        return i2


class HL123_CFG2_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['amount','high', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '(-0.5, 1]'# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):

        amount = data['amount'].iloc[-120:]
        df_s = amount.sum(axis = 0)
        bool_df = df_s.gt((df_s.quantile(0.90))).values.astype(float)
        bool_df[bool_df==0] = np.nan
        
        hlow = data['low_preadj'].iloc[-110:]
        hhigh = data['high_preadj'].iloc[-110:]
        hhigh_s = hhigh.shift(30).values
        hlow_s = hlow.shift(30).values
        
        hlow = hlow.iloc[-76:].values
        hhigh = hhigh.iloc[-76:].values
        
        i11 = (bk.move_max(hhigh, 10, min_count = 5, axis = 0)-bk.move_min(hlow, 60, min_count = 10, axis = 0))[-15:]
        i12 = (bk.move_max(hhigh_s, 10, min_count = 5, axis = 0)-bk.move_min(hlow_s, 60, min_count = 10, axis = 0))[-15:]
        i2 = np.nanmean((i11-i12)*bool_df)
        
        return i2


#####################################################################################
        
class HcorrC_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','weight','high', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):

        hhigh = data['high_preadj'].iloc[-60:]
        hclose = data['close_preadj'].iloc[-60:]
        hweight = data['weight'].iloc[-1]
        
        t_pcor2 = hhigh.corrwith(hclose)

        t_pcor2[~np.isfinite(t_pcor2)] = 0
        
        factor = np.nanmean(t_pcor2*hweight)
        return factor

#####################################################################################


class L123_CC_nr_ae_CFG_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 11
    data_dict = dict()
    data_dict['Stock'] = ['amount','turnover_rate','low','adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        amount = data['amount'].iloc[-165:, :]
        turnover = data['turnover_rate'].iloc[-165:, :]
        df_s = (amount.rolling(120, min_periods = 15).sum())
        ret_30 = (turnover/turnover.shift(30)-1)
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0)

        temp5 = ret_30.gt(pd.Series(ret_30.quantile(0.80, axis = 1)), axis=0)
        mask = (temp1*temp5).values[-40:]
        
        hlow = data['low_preadj'].values[-1400:]
        i11 = bk.move_min(hlow, 10, min_count = 5, axis = 0) - bk.move_min(hlow, 25, min_count = 10, axis = 0)
        i12 = bk.move_min(hlow, 20, min_count = 15, axis = 0) - bk.move_min(hlow, 30, min_count = 10, axis = 0)
        i2 = (i11-i12)
        
        i_temp = rolling_norm(i2)[-40:]

        ii2 = i_temp*mask

        factor = np.nansum(ii2, axis = 1)
        factor = np.nanmean(factor)
        
        return factor


class L123_CC_nr_vs_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','weight','low', 'high', 'adjfactor']
    normalize_size = 720 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        stk_close = data['close_preadj'].iloc[-73:]
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = ts_std(stk_ret, 30)
        mask = (stk_volatility).values[-40:]
        hlow = data['low_preadj'].iloc[-1400:].values
        i11 = bk.move_min(hlow, 10, min_count = 5, axis = 0) - bk.move_min(hlow, 25, min_count = 10, axis = 0)
        i12 = bk.move_min(hlow, 20, min_count = 15, axis = 0) - bk.move_min(hlow, 30, min_count = 10, axis = 0)
        i2 = (i11-i12)
        
        i_temp = rolling_norm(i2)[-40:]
        
        ii2 = i_temp*mask

        factor = np.nansum(ii2, axis = 1)    
        factor = np.nanmean(factor)
        return factor
    
    
class L123_CFG2_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','weight','low', 'high', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        amount = data['amount'].iloc[-120:]
        df_s = amount.sum(axis = 0)
        stk_amount = df_s.gt(df_s.quantile(0.90))
        
        index_close = data['close_000905.SH'].iloc[-1203:]
        stk_close = data['close_preadj'].iloc[-1203:]
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.iloc[-1200:].corrwith(index_ret.iloc[-1200:, 0])
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        mask = (stk_index_corr*stk_amount).values
        
        hlow = data['low_preadj'].iloc[-55:].values
        i11 = bk.move_min(hlow, 10, min_count = 5, axis = 0) - bk.move_min(hlow, 25, min_count = 10, axis = 0)
        i12 = bk.move_min(hlow, 20, min_count = 15, axis = 0) - bk.move_min(hlow, 30, min_count = 10, axis = 0)
        i2 = np.nanmean((i11-i12)[-25:], axis = 0)
    
        ii2 = i2*mask

        factor = np.nanmean(ii2)
        
        return factor
    

class L123_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','weight','low', 'high', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        hlow = data['low_preadj'].iloc[-65:].values
        i11 = bk.move_min(hlow, 10, min_count = 5, axis = 0) - bk.move_min(hlow, 25, min_count = 10, axis = 0)
        i12 = bk.move_min(hlow, 20, min_count = 15, axis = 0) - bk.move_min(hlow, 30, min_count = 10, axis = 0)
        i2 = np.nanmean((i11-i12)[-30:], axis = 0)

        factor = np.nanmean(i2)
        
        return factor


class LMLS_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','weight','low', 'high', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):

        index_close = data['close_000905.SH'].iloc[-1203:]
        stk_close = data['close_preadj'].iloc[-1203:]
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.iloc[-1200:].corrwith(index_ret.iloc[-1200:, 0])
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        stk_index_corr_rank = 2 * stk_index_corr.rank(pct=True) - 1
        
        hlow = data['low_preadj'].iloc[-51:]
        hlow_s = hlow.shift(20).iloc[-30:].values
        hlow = hlow.iloc[-50:].values
        i2 = np.nanmean(hlow, axis = 0) - np.nanmean(hlow_s, axis = 0)
        ii2 = np.nanmean(i2*stk_index_corr_rank.values)

        return ii2


class LSC_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 8
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','weight','low', 'high', 'adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        amount = data['amount'].iloc[-125:]
        df_s = amount.rolling(120, min_periods = 15).sum()
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0).iloc[-3:].values
        
        
        index_close = data['close_000905.SH'].iloc[-1206:]
        stk_close = data['close_preadj'].iloc[-1206:]
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = (stk_ret.iloc[-1204:].rolling(1200, min_periods=1200).corr(index_ret.iloc[-1204:,0])).iloc[-3:]
        
        stk_index_corr = (stk_index_corr.replace([-np.inf, np.inf], np.nan)).values
        bool_df = (stk_index_corr*stk_amount)
        
        hhigh = data['high_preadj'].values[-55:]
        hclose = data['close_preadj'].values[-55:]
        hlow = data['low_preadj'].values[-55:]
        
        h = bk.move_max(hhigh, 30, min_count = 10, axis = 0)
        l = bk.move_min(hlow, 30, min_count = 10, axis = 0)
        hld = h - l
        
        hh = (h-hclose)/(hld)
        ll = (hclose-l)/(hld)
        
        hh[abs(hh)>100000] = np.nan
        ll[abs(ll)>100000] = np.nan
        
        vwtc_r = (bk.move_mean(ll, 15, min_count = 5, axis = 0) - bk.move_mean(hh, 15, min_count = 5, axis = 0))[-3:]
        factor = np.nanmean(vwtc_r*bool_df, axis = 1)
        factor = np.nanmean(factor)
        return factor



class LminC_CFG3_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'low', 'weight', 'adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        index_close = data['close_000905.SH'].iloc[-1203:]
        stk_close = data['close_preadj'].iloc[-1203:]
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.iloc[-1200:].corrwith(index_ret.iloc[-1200:, 0])
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        
        cs2 = stk_index_corr.gt(stk_index_corr.quantile(0.90)).values
            
        hlow = np.nanmin(data['low_preadj'].iloc[-180:], axis = 0)
        hclose = data['close_preadj'].iloc[-1]
        
        factor = np.nanmean(((-hlow/hclose))[cs2])
        
        return factor
    


class OCtHL_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'low', 'high','open', 'amount', 'adjfactor']
    normalize_size = 1000 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        

        hopen = data['open_preadj'].iloc[-120:].values
        hhigh = data['high_preadj'].iloc[-120:].values
        hclose = data['close_preadj'].iloc[-120:].values
        hlow = data['low_preadj'].iloc[-120:].values
        hamount = data['amount'].iloc[-120:]
        
        df_s = hamount.sum(axis = 0)

        stk_amount = df_s.gt((df_s.quantile(0.90)))
        temp1 = hopen - hclose
        temp2 = hhigh - hlow
        t_pcor2 = -temp1/temp2
        t_pcor2[abs(t_pcor2)>10000] = np.nan
        t_pcor2 = bk.move_mean(t_pcor2, 45, min_count = 15, axis =0)#.rolling(5, min_periods = 2).mean()
        factor = (t_pcor2[-1]*stk_amount).mean()
        
        return factor
    


class RolTrendLS_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 10
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'low', 'high','open', 'amount', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):

        hhigh = data['high_preadj'].iloc[-145:].values
        hclose = data['close_preadj'].iloc[-145:].values
        hlow = data['low_preadj'].iloc[-145:].values
        
        amount = data['amount'].iloc[-127:]
        df_s = amount.rolling(120, min_periods = 15).sum()
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0).iloc[-5:]

        index_close = data['close_000905.SH'].iloc[-1208:]
        stk_close = data['close_preadj'].iloc[-1208:]
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = (stk_ret.iloc[-1206:].rolling(1200, min_periods=1100).corr(index_ret.iloc[-1206:,0])).iloc[-5:]
        stk_index_corr = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0)
        
        stk_index_corr = (stk_index_corr.replace([-np.inf, np.inf], np.nan))
        bool_df = (stk_index_corr*stk_amount).astype(float)
        bool_df[bool_df==0] = np.nan
        
        l = bk.move_min(hlow, 120, min_count = 15, axis = 0)
        h = bk.move_max(hhigh, 120, min_count = 15, axis = 0)
        
        a = h - l
        a[abs(a)<1e-8] = np.nan
        
        ll = (hclose - l) / a
        a2 = bk.move_mean(ll, 10, min_count = 5, axis = 0)
        a3 = bk.move_mean(a2, 10, min_count = 5, axis = 0)
        vwtc_r = (3*a3-2*a2)[-5:]

        factor = np.nanmean(vwtc_r*bool_df, axis = 1)
        factor = np.nanmean(factor)
        
        return factor 

#
class SYXWR_ar_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'low', 'high','open', 'weight', 'adjfactor']
    normalize_size = 2400 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        hopen = data['open_preadj'].iloc[-85:].values
        hhigh = data['high_preadj'].iloc[-85:].values
        hclose = data['close_preadj'].iloc[-85:].values
        hlow = data['low_preadj'].iloc[-85:].values
        
        amount = data['amount'].iloc[-50:]      
        stk_amount_rank = (2 * amount.rank(axis=1, pct=True) - 1)
        
        temp1 = (np.where(hopen>hclose, hopen, hclose))
        
        b = bk.move_mean((hhigh - temp1), 30, min_count = 15, axis = 0)
        b[abs(b)<1e-8] = np.nan
        t_pcor = (hhigh - temp1)/b
        h = bk.move_max(hhigh, 30, min_count = 15, axis = 0)
        l = bk.move_min(hlow, 30, min_count = 15, axis = 0)
        a = h-l
        t_pcor2 = (hclose-l)/a
        t_pcorr = (t_pcor2 - t_pcor)[-50:]
        t = np.nansum(t_pcorr * stk_amount_rank, axis = 1)
        factor = bk.move_sum(t, 40, min_count = 20, axis = 0)
        factor = factor[-1]
        
        return factor
    
#
class VLSM_CFG2_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','amount', 'low', 'high','open', 'weight','volume' 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '(-0.5, 1]'# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        

        hamount = data['amount'].iloc[-1500:]
        hvolume = data['volume_preadj'].iloc[-1500:].values      
        bool_df = (2 * hamount.rank(axis=1, pct=True) - 1).iloc[-1250:].values
        hamount = hamount.values
        
        vwap = hamount/hvolume
        price_diff_1 = (vwap[1:]/vwap[:-1]-1)[-1250:]
        price_diff_30 = (vwap[30:]/vwap[:-30]-1)[-1250:]
        copcor1_r = -(price_diff_1-price_diff_30)
        
        factor = np.nanmean(bool_df*copcor1_r, axis = 1)

        factor = bk.move_mean(factor, 10, min_count = 1)
        factor = ts_rank(factor[-1202:])

        return factor[-1]


#
class VLSM_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','amount', 'low', 'high','open', 'weight','volume' 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '(-0.5, 1]'# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀

    def calculate(self, data):
        
        hopen = data['open_preadj'].iloc[-85:].values
        hhigh = data['high_preadj'].iloc[-85:].values
        hclose = data['close_preadj'].iloc[-85:].values
        hlow = data['low_preadj'].iloc[-85:].values
        
        amount = data['amount'].iloc[-120:]
        df_s = amount.sum(axis = 0)
        stk_amount = df_s.gt(df_s.quantile(0.90)).astype(float)
        stk_amount[stk_amount==0] = np.nan
        
        temp1 = (np.where(hopen>hclose, hopen, hclose))
        
        b = bk.move_mean((hhigh - temp1), 40, min_count = 15, axis = 0)
        b[abs(b)<1e-8] = np.nan
        t_pcor = (hhigh - temp1)/b
        h = bk.move_max(hhigh, 40, min_count = 15, axis = 0)
        l = bk.move_min(hlow, 40, min_count = 15, axis = 0)
        a = h-l
        a[abs(a) < 1e-8] = np.nan
        t_pcor2 = (hclose-l)/a
        t_pcorr = bk.move_mean((t_pcor2 - t_pcor)[-41:], 40, min_count = 20, axis = 0)[-1]
        t = np.nanmean(t_pcorr[stk_amount])
        
        return t
    
#
class VwLs_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','amount', 'low', 'high','open', 'weight','volume' 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '(-0.5, 1]'# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀

    def calculate(self, data):
        

        hamount = data['amount'].iloc[-120:]
        hvolume = data['volume_preadj'].iloc[-120:].values      

        df_s = hamount.sum(axis = 0)
        bool_df = df_s.gt(df_s.quantile(0.90)).values
        
        hamount = hamount.values
        
        vwap = hamount/hvolume
        price_diff_1 = (vwap[1:]/vwap[:-1]-1)[-5:]
        price_diff_90 = (vwap[90:]/vwap[:-90]-1)[-5:]
        copcor1_r = -np.nanmean((price_diff_1-price_diff_90), axis = 0)
        
        factor = np.nanmean(bool_df*copcor1_r)

        return factor
    
#
class ZHZH_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','amount', 'low', 'high','open', 'weight','volume' 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀

    def calculate(self, data):
        

        hamount = data['amount'].iloc[-120:]
        hhigh = data['high_preadj'].iloc[-75:].values      

        df_s = hamount.sum(axis = 0).astype(float)
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        bool_df[bool_df==0] = np.nan
        bool_df = df_s.gt(df_s.quantile(0.90))
        
        a = (hhigh>=(bk.move_max(hhigh, 30, min_count = 5, axis = 0)))
        temp = np.nanmean(a[-40:], axis = 0)
        #temp = temp.iloc[-1]
        #temp = np.nanmean(((hhigh>=(bk.move_mean(hhigh, 30, min_count = 5, axis = 0))))[-40:], axis = 0)
        temp = np.nanmean(temp*bool_df)
        
        return temp

#
class cmh_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 10
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','amount', 'low', 'high','open', 'weight','volume' 'adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '(-0.5, 1]'# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀

    def calculate(self, data):
        
        index_close = data['close_000905.SH'].iloc[-2208:]
        stk_close = data['close_preadj'].iloc[-2208:]
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = (stk_ret.iloc[-2206:].rolling(1200, min_periods=600).corr(index_ret.iloc[-2206:,0]))
        
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        bool_df = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0).astype(float).values[-1005:]
        bool_df[bool_df==0] = np.nan
        

        hhigh = data['high_preadj'].iloc[-2270:].values  
        hclose = data['close_preadj'].iloc[-2270:].values 
        
        vwtc_r = (hhigh-bk.move_mean(hclose, 60, min_count = 30, axis = 0))[-1005:]
 
        factor = np.nanmean(vwtc_r*bool_df, axis = 1)
        
        factor = ts_rank(factor, 1000)
        factor = np.nanmean(factor[-2:])
               
        return factor

#
class cmh_ae_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 10
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','amount', 'low', 'high', 'turnover_rate', 'adjfactor']
    normalize_size = 242 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀

    def calculate(self, data):
        
        turnover = data['turnover_rate'].iloc[-46:]
        amount = data['amount'].iloc[-131:]
        
        df_s = (amount.rolling(120, min_periods = 15).sum())
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0).iloc[-10:].values
        ret_30 = (turnover/turnover.shift(30)-1)
        ret_30 = ret_30.replace([-np.inf, np.inf], np.nan)
        temp5 = ret_30.gt(pd.Series(ret_30.quantile(0.80, axis = 1)), axis=0).iloc[-10:].values

        bool_df = (temp1&temp5)
        
        hhigh = data['high_preadj'].iloc[-1335:].values  
        hclose = data['close_preadj'].iloc[-1335:].values 
        
        vwtc_r = (hhigh-bk.move_mean(hclose, 120, min_count = 30, axis = 0))
        vr = rolling_norm(vwtc_r)[-10:]
        
        factor = np.nanmean(vr*bool_df, axis = 0)
        factor = np.nanmean(factor)
               
        return factor
#
class hhll_CFG2_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'low', 'high', 'adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        index_close = data['close_000905.SH'].iloc[-1203:]
        stk_close = data['close_preadj'].iloc[-1203:]
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.iloc[-1200:].corrwith(index_ret.iloc[-1200:, 0])
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        bool_df = stk_index_corr.gt((stk_index_corr.quantile(0.90))).astype(float)
        bool_df[bool_df==0] = np.nan

        hhigh = data['high_preadj'].iloc[-45:].values
        hlow = data['low_preadj'].iloc[-45:].values
        
        d1 = hhigh[1:]>hhigh[:-1]
        d2 = hlow[1:]>hlow[:-1]
        
        d_f = (d1.astype(int)+d2.astype(int))
        d_f[d_f == 2] = 4
        
        vwtc_r = np.nanmean(d_f[-40:], axis = 0)
        factor = np.nanmean(vwtc_r*bool_df)
        
        return factor
#
class hhll_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['amount', 'low', 'high', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        hamount = data['amount'].iloc[-120:]
        df_s = hamount.sum(axis = 0)
        stk_amount = df_s.gt(df_s.quantile(0.90)).astype(float)
        stk_amount[stk_amount==0] = np.nan

        hhigh = data['high_preadj'].iloc[-45:].values
        hlow = data['low_preadj'].iloc[-45:].values
        
        d1 = hhigh[1:]>hhigh[:-1]
        d2 = hlow[1:]>hlow[:-1]
        
        d_f = (d1.astype(int)+d2.astype(int))
        d_f[d_f == 2] = 4
        
        vwtc_r = np.nanmean(d_f[-25:], axis = 0)
        factor = np.nanmean(vwtc_r*stk_amount)
        
        return factor
    
#
class hhll_ind_CC_nr_ct_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','turnover_rate','low', 'high', 'stk_index_corr_zz500', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        tover = data['turnover_rate'].iloc[-100:]       
        turnover = (tover.rolling(60, min_periods = 15).mean())[-31:]
        stk_index_corr = data['stk_index_corr_zz500'].iloc[-31:]        
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        tempp2 = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.80, axis = 1)), axis=0).values
        tempp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0).values
        
        hhigh = data['high_preadj'].iloc[-1235:].values
        hlow = data['low_preadj'].iloc[-1235:].values
        
        d1 = (hhigh[1:]>hhigh[:-1])
        d2 = (hlow[1:]>hlow[:-1])
        
        d_f = (d1.astype(int)+d2.astype(int))
        d_f[d_f == 2] = 4
        
        factor1 = rolling_norm(d_f)[-31:]
        
        mask = (tempp2 * tempp4).astype(float)
        mask[mask==0] = np.nan
        factor = np.nanmean(factor1*mask, axis = 1)
        
        factor = np.nanmean(factor[-30:])
        return factor

#
class updown_cfg2_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['amount', 'close','adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        amount = data['amount'].iloc[-215:]        
        df_s = (amount.rolling(120, min_periods = 15).sum())
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0).astype(float)
        stk_amount[stk_amount==0] = np.nan
        hclose_o = data['close_preadj'].iloc[-216:].values
        
        hclose = (hclose_o[1:]/hclose_o[:-1]-1)
        upclose = np.nansum(stk_amount*((hclose>0).astype(int)), axis = 1)
        downclose = np.nansum(stk_amount*((hclose<0).astype(int)), axis = 1)

        vwtc_r = np.nanmean(((upclose-downclose)/ (upclose+downclose))[-90:], axis = 0)
        if abs(vwtc_r)>10000:
            vwtc_r = np.nan
        
        return vwtc_r


class updown_cfg4_2_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','volume', 'amount' ,'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        amount = data['amount'].iloc[-160:]        
        df_s = (amount.rolling(120, min_periods = 15).sum())
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0).values.astype(float)
        stk_amount[stk_amount==0]=np.nan
        #df_s = bk.move_sum(amount, 120, min_count = 15, axis = 0)
        #stk_amount = df_s.argsort().argsort()>=(np.shape(df_s)[-1]*0.9)
        
        hclose_o = data['close_preadj'].iloc[-161:].values
        hvolume_o = data['volume_preadj'].iloc[-161:].values
        
        hc = (hclose_o[1:]/hclose_o[:-1]-1)*(stk_amount)
        hcv = (hvolume_o[1:]/hvolume_o[:-1]-1)*(stk_amount)
        upclose = np.nansum((hc>0).astype(int), axis = 1)
        downclose = np.nansum((hc<0).astype(int), axis = 1)
        upvolume = np.nansum((hcv>0).astype(int), axis = 1)
        downvolume = np.nansum((hcv<0).astype(int), axis = 1)
        
        aa = (upclose/downclose)
        aa[abs(aa)>100000] = np.nan
        bb = (upvolume/downvolume)
        bb[abs(bb)>100000] = np.nan
        vwtc_r = (aa/bb)
        vwtc_r[abs(vwtc_r)>100000] = np.nan
        factor = np.nanmean(vwtc_r[-35:])
        return factor


class updown_cfg4_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','volume', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        hclose_o = data['close_preadj'].iloc[-36:].values
        hvolume_o = data['volume_preadj'].iloc[-36:].values
        
        hc = (hclose_o[1:]/hclose_o[:-1]-1)
        hcv = (hvolume_o[1:]/hvolume_o[:-1]-1)
        upclose = np.nansum((hc>0).astype(int), axis = 1)
        downclose = np.nansum((hc<0).astype(int), axis = 1)
        upvolume = np.nansum((hcv>0).astype(int), axis = 1)
        downvolume = np.nansum((hcv<0).astype(int), axis = 1)
        
        aa = (upclose/downclose)
        aa[abs(aa)>100000] = np.nan
        bb = (upvolume/downvolume)
        bb[abs(bb)>100000] = np.nan
        vwtc_r = (aa/bb)
        vwtc_r[abs(vwtc_r)>100000] = np.nan
        factor = np.nanmean(vwtc_r)
        return factor


        
class vol_diff_zsj(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'turnover_rate', 'low', 'high']
    normalize_size = 242*5 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = '(-0.85, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        stk_close = data['close_preadj'].iloc[-61:].values
        stk_volume = data['volume_preadj'].iloc[-60:].values
        stk_close[abs(stk_close) < 1e-8] = np.nan
        
        stk_ret = (stk_close[1:] / stk_close[:-1] - 1)
        up_mask = (stk_ret > 0).astype(float)
        down_mask = (stk_ret < 0).astype(float)
        up_vol = np.nansum(stk_volume*up_mask, axis = 1)
        down_vol = np.nansum(stk_volume*down_mask, axis = 1)
        vol_diff_raw = up_vol - down_vol
        factor = np.nanmean(vol_diff_raw)
        return factor
    

class vwap_ma_zsj(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['high','low', 'close', 'volume']} 
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = '[0, 1]'
    
    def calculate(self, data):
        close = data['close_cont_IC'].iloc[-80:]
        high = data['high_cont_IC'].iloc[-80:]
        low = data['low_cont_IC'].iloc[-80:]
        volume = data['volume_cont_IC'].iloc[-80:]

        ##### calc factor #####
        def calc_vwap_sig(close, high, low, volume, roll_win):
            typical = (high + low + close) / 3
            mf = volume * typical
            volume_sum = bk.move_sum(volume, roll_win, min_count = 1, axis = 0)
            volume_sum[abs(volume_sum)<1e-8] = np.nan
            mf_sum = bk.move_sum(mf, roll_win, min_count = 1, axis = 0)
            vwap_val = mf_sum / volume_sum
            vwap_diff = close - vwap_val
            return vwap_diff


        roll_win = 15
        ma_win = 60

        score_raw = calc_vwap_sig(close, high, low, volume, roll_win)
        factor = np.nanmean(score_raw[-ma_win:])
        return factor