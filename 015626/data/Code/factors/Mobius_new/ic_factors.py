import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_cfg11(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'weight', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '(-0.5,1]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-25:]
        stk_weight = data['weight'].values[-25:]
        stk_ret = ts_pct_change(stk_close, 5)
        ret_mean = ts_mean(stk_ret, 20)
        ret_std = ts_std(stk_ret, 20)
        factor_init = ret_mean + ret_std
        factor_raw = np.nansum(factor_init * stk_weight, axis=1)
        return factor_raw[-1]
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:30:37 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


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
##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

class high_low_diff_a2p_zsj(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 11
    data_dict = dict()
    data_dict['Stock'] = ['close','adjfactor','amount','open','high','low']
    normalize_size = 800
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        stk_close = data['close_preadj'][-2460:]
        stk_high = data['high_preadj'][-2460:]
        stk_low = data['low_preadj'][-2460:]
        stk_open = data['open_preadj'][-2460:]
        stk_amt = data['amount'][-2460:]

        cut_line = stk_amt.median(axis=1)
        active_mask = stk_amt.subtract(cut_line, axis=0) >= 0
        inactive_mask = stk_amt.subtract(cut_line, axis=0) < 0

        high_open_diff = stk_high - stk_open
        open_low_diff = stk_open - stk_low
        high_low_diff_stk = high_open_diff.rolling(30, 27).sum() - open_low_diff.rolling(30, 27).sum()
        high_low_diff_active_raw = high_low_diff_stk[active_mask].mean(axis=1)[-2430:]
        high_low_diff_inactive_raw = high_low_diff_stk[inactive_mask].mean(axis=1)[-2430:]
        high_low_diff_a2p_raw = (high_low_diff_active_raw - high_low_diff_inactive_raw).values
        ma = bk.move_mean(high_low_diff_a2p_raw, 30, min_count=27, axis = 0)[-2400:]
        ts_dat_pct_np = bk.move_rank(ma, window=2400, min_count=2160, axis=0)
        factor = (ts_dat_pct_np[-1] + 1) / 2
        return factor
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class csv_disp_sign_zsj(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'adjfactor'] 
    normalize_size = 1210
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        stk_close = data['close_preadj'][-131:]
        stk_ret = (stk_close / stk_close.shift(1) - 1)
        csv_disp = stk_ret.std(axis=1)
        stk2idx_ret = stk_ret.mean(axis=1)
        csv_disp_sign_raw = csv_disp * np.sign(stk2idx_ret)
        factor = np.nanmean(csv_disp_sign_raw[-130:].values)
        return factor
##########
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_cc import *
from operators_wsc_1_0 import *
from future_factor import FutureFactor


def ts_truncated_ema_1(data, d, alpha):
    # truncated ema
    if (alpha >= 1) or (alpha <= 0):
        raise ValueError('`alpha` must be in (0, 1)')
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    return ts_decay_linear(data=data, d=d, weight=weight)


def ts_truncated_ema_span_1(data, d, span):
    # truncated ema
    return ts_truncated_ema_1(data=data, d=d, alpha=2 / (span + 1))


class Short_BS_Main_CFG5_CC(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_midorder_count', 'buy_smallorder_count', 'weight', 'close']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False

    def calculate(self, data):
        stk_close = data['close'].values[-127:]
        stk_weight = data['weight'].values[-127:]
        skt_buy_midorder_count = data['buy_midorder_count'].fillna(0).values[-127:]
        stk_buy_smallorder_count = data['buy_smallorder_count'].fillna(0).values[-127:]
        
        
        df_s = bk.move_sum(skt_buy_midorder_count + stk_buy_smallorder_count, 5, 2, axis=0) * stk_weight
        df_s[stk_weight <= 0] = np.nan
        hret = ts_pct_change(stk_close, 1)
        hret = ts_truncated_ema_span_1(hret, 120, 20)
        df_s_mask = np.nanmedian(df_s, axis=1)
        df_s_mask = np.expand_dims(df_s_mask, axis=-1)
        hret_1 = ma.array(hret, mask=(df_s<=df_s_mask))
        hret_2 = ma.array(hret, mask=(df_s>=df_s_mask))
        temp2 = np.nanmean(hret_1, axis=1) - np.nanmean(hret_2, axis=1)
        return temp2[-1]
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk

def get_norm(fa):
    fmax = np.nanmax(fa)
    fmin = np.nanmin(fa)
    divisor = fmax - fmin
    if divisor < 1e-8:
        divisior = np.nan
    return ((fa[-1] - fmin)/ divisor) * 2 - 1

class wyc_icif(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close'],'IF':['close']} 
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 
 
    def calculate(self, df):
        factor = (df['close_cont_IC'] - df['close_cont_IF']).values
        factor = factor - bk.move_mean(factor, 240, min_count = 120, axis = 0)
        factor = bk.move_mean(factor, 20, min_count = 10, axis = 0)
        factor = get_norm(factor[-5*242:])
        return factor


##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd
import scipy

class Short_BS10_2_CC(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Stock'] = ['close','buy_superorder_count','buy_bigorder_count','buy_midorder_count','buy_smallorder_count']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = False

    def calculate(self, data):
        index_close = data['close_000905.SH'][-1203:]
        stk_close = data['close'][-1203:]
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.iloc[-1200:].corrwith(index_ret.iloc[-1200:,0])
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        bool_df = stk_index_corr[stk_index_corr>stk_index_corr.quantile(0.9)]
        bool_stk_list = bool_df.index.to_list()
        
        a = data['buy_superorder_count'][-4:].fillna(0) + data['buy_bigorder_count'][-4:].fillna(0) + data['buy_midorder_count'][-4:].fillna(0) + data['buy_smallorder_count'][-4:].fillna(0)
        temp2 = (data['buy_smallorder_count'][-4:]).fillna(0)/ a.replace(0, np.nan)
        temp2 = temp2.replace([-np.inf, np.inf], np.nan)
        factor = np.nanmean(temp2[bool_stk_list].values * -1,axis = 1)
        factor = np.nanmean(factor)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:22:51 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


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
##########
from future_factor import FutureFactor
from operators_wsc_1_0 import *


class wsc1_future_kpz(FutureFactor):
    data_type = 'Future'
    days_past = 2
    data_dict = dict()
    instrument_type = 'recent'
    # data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Continuous_Data'] = {'IF':['close']}
    normalize_size = 0
    normalize_type = 'rolling_norm'
#    num_range = '[0,1]'
    
    def calculate(self, data):
        future_close = data['close_cont_IF'].values[-240:]
        factor_init = log(future_close)
        factor_raw = rolling_norm(factor_init, 240)
        return factor_raw[-1]




##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd
import scipy


class Short_BS9_2_CC(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Stock'] = ['close','buy_superorder_count','buy_bigorder_count','buy_midorder_count','buy_smallorder_count']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = False

    def calculate(self, data):
        index_close = data['close_000905.SH'][-1203:]
        stk_close = data['close'][-1203:]
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.iloc[-1200:].corrwith(index_ret.iloc[-1200:,0])
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        bool_df = stk_index_corr[stk_index_corr>stk_index_corr.quantile(0.9)]
        bool_stk_list = bool_df.index.to_list()
        
        a = data['buy_superorder_count'][-5:].fillna(0) + data['buy_bigorder_count'][-5:].fillna(0) + data['buy_midorder_count'][-5:].fillna(0) + data['buy_smallorder_count'][-5:].fillna(0)
        temp2 = (data['buy_bigorder_count'][-5:].fillna(0) + data['buy_superorder_count'][-5:].fillna(0))/ a.replace(0, np.nan)
        temp2 = temp2.replace([-np.inf, np.inf], np.nan)
        factor = np.nanmean(temp2[bool_stk_list].values,axis = 1)
        factor = np.nanmean(factor)
        
        return factor
##########
from future_factor import FutureFactor
from operators_wsc_1_0 import *
    

class wsc4_future_kpz(FutureFactor):
    data_type = 'Future'
    days_past = 6
    data_dict = dict()
    instrument_type = 'recent'
    # data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Continuous_Data'] = {'IF':['close']}
    normalize_size = 1
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        future_close = data['close_cont_IF'].values[-1322:]
        N = 20
        dpo = future_close - ts_delay(ts_mean(future_close, N), int(N/2+1))
        factor_init = abs(dpo - ts_median(dpo, 60))
        factor_mean = ts_mean(factor_init, 30)
        factor_raw = ts_rank(factor_mean, 1200)
        return factor_raw[-1]

##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

def rolling_norm(sig, window=1200, method='max_min'):
    assert isinstance(sig, pd.Series) or isinstance(sig, pd.DataFrame) or isinstance(sig, np.ndarray), 'input must be a series, dataframe or ndarray'
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
            elif isinstance(sig, np.ndarray):
                sig_max = bk.move_max(sig, window=window, min_count=int(window / 2), axis=0)
                sig_min = bk.move_min(sig, window=window, min_count=int(window / 2), axis=0)
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
            elif isinstance(sig, np.ndarray):
                output = bk.move_rank(sig, window=d, min_count=int(d / 2), axis=0)
            return signal
        
        
class wyc_ts50_future_nr_tr(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 12
    data_dict = dict()
    data_dict['Stock'] = ['close', 'turnover_rate', 'adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[-1,0]'
    handle_preadj = True
    
    def calculate(self, df):
        close = df['close_preadj'][-2820:].values
        returns = close[1:] / close[:-1] - 1
      
        factor = bk.move_sum((returns>0), 20, 10, axis = 0)[-2800:]
        factor = bk.move_mean(factor, 20, 10, axis = 0)[-2780:]
        factor = bk.move_rank(factor, 1210, 605, axis = 0)[-1570:]

        factor = rolling_norm(factor, 5 * 242)[-360:]

        t = df['turnover_rate'][-360:]
        tr = (2 * t.rank(axis=1, pct=True) - 1)
        factor = factor * tr
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 300, 150, axis = 0)[-60:]
        factor = np.nanmean(factor)

        return factor
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc15_cfg_vs(FutureFactor):
    data_type = 'IndexStock'
    days_past = 2
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'stk_volatility', 'adjfactor']
    normalize_size = 1800
    normalize_type = 'ts_rank'
#    num_range = '(-0.3,1]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-256:]
        stk_volatility = data['stk_volatility'].values[-256:]
        n = 10
        temp = ts_sum(abs(ts_delta(stk_close, 1)), n)
        vi = abs(ts_delta(stk_close, n)) / replace_zero(temp)
        vidya = vi * stk_close + (1-vi) * ts_delay(stk_close, 1)
        factor_init = rolling_norm(vidya, 240)
        factor_raw = np.nansum(factor_init * stk_volatility, axis=1)
        return factor_raw[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:03:40 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

#
class VLSM_CFG2_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','amount','volume', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.5, 1]'# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
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
##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

class ret_active2inactive_zsj(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close','adjfactor','amount']
    normalize_size = 1200
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        stk_close = data['close_preadj'][-181:]
        stk_amt = data['amount'][-181:]
        stk_ret = (stk_close / stk_close.shift(1) - 1)
        cut_line = stk_amt.median(axis=1)
        active_mask = stk_amt.subtract(cut_line, axis=0) >= 0
        inactive_mask = stk_amt.subtract(cut_line, axis=0) < 0
        ret_active_raw = stk_ret[active_mask].mean(axis=1)
        ret_inactive_raw = stk_ret[inactive_mask].mean(axis=1)
        ret_active2inactive_raw = (ret_active_raw - ret_inactive_raw).values[-180:]
        factor = np.nanmean(ret_active2inactive_raw)
        return factor
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *


    
class wsc_hf17(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['Bid1AmtMean', 'Buy1NumOrdersMean']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        stk_Bid1AmtMean = data['Bid1AmtMean'].values[-1]
        stk_Buy1NumOrdersMean = data['Buy1NumOrdersMean'].values[-1]
        factor_raw = np.nansum(stk_Bid1AmtMean) / np.nansum(stk_Buy1NumOrdersMean)
        return factor_raw
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk

def get_norm(fa):
    fmax = np.nanmax(fa)
    fmin = np.nanmin(fa)
    divisor = fmax - fmin
    if divisor < 1e-8:
        divisior = np.nan
    return ((fa[-1] - fmin)/ divisor) * 2 - 1

class wyc_if_2hour_return(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['close']} 
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[0,1]'
    handle_preadj = None 

    def calculate(self, df):
        cif = df['close_cont_IF'].values
        ifreturn = cif[1:] / cif[:-1] - 1
        factor = bk.move_mean(ifreturn, 200, min_count=100, axis = 0)
        factor = get_norm(factor[-5 * 242:])
        return factor
##########
import numpy as np
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


class wsc_fast10_cfg(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['open', 'close', 'high', 'weight', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_open = data['open_preadj'].values[-30:]
        stk_close = data['close_preadj'].values[-30:]
        stk_high = data['high_preadj'].values[-30:]
        stk_weight = data['weight'].values[-30:]

        x = stk_close - stk_open
        y = np.where(x>0, stk_close, stk_open)
        z = replace_zero(stk_high - y)
        u = x / z
        factor_raw = np.nansum(u * stk_weight, axis=1)
        factor_mean = ts_mean(factor_raw, 30)       
        return factor_mean[-1]
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc13_cfg_ar(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'volume', 'adjfactor']
    normalize_size = 2000
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-55:]
        stk_volume = data['volume_preadj'].values[-55:]
        amount_rank_mask = section_rank_np(stk_amount, pct=True) * 2 - 1
        stk_vwap = stk_amount / replace_zero(stk_volume)
        vwap_ma = ts_mean(stk_vwap, 45)
        amount_ma = ts_mean(stk_amount, 45)
        volume_ma = replace_zero(ts_mean(stk_volume, 45))
        temp = replace_zero(amount_ma / volume_ma)
        apb = vwap_ma / temp
        factor_init = -np.log(apb)
        factor_raw = np.nansum(factor_init * amount_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 10)
        return factor_mean[-1]
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd
from joblib import Parallel, delayed

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
    assert isinstance(df, pd.DataFrame), 'the data structure of input is illegal, must be dataframe'
    results = Parallel(n_jobs=n_jobs)(delayed(func)(df[i], **kwargs) for i in df.columns)
    results_df = pd.DataFrame(results, index=df.columns, columns=df.index)
    return results_df.T

def rolling_norm(sig, window=1200, method='max_min'):
    assert isinstance(sig, pd.Series) or isinstance(sig, pd.DataFrame) or isinstance(sig, np.ndarray), 'input must be a series, dataframe or ndarray'
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
            elif isinstance(sig, np.ndarray):
                sig_max = bk.move_max(sig, window=window, min_count=int(window / 2), axis=0)
                sig_min = bk.move_min(sig, window=window, min_count=int(window / 2), axis=0)
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
            elif isinstance(sig, np.ndarray):
                output = bk.move_rank(sig, window=d, min_count=int(d / 2), axis=0)
            return signal
        
class wyc_ts6_future_nr_cr(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 12
    data_dict = dict()
    data_dict['Stock'] = ['close', 'stk_index_corr_zz500', 'high', 'low', 'volume', 'adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[0,1]'
    handle_preadj = True 

    def calculate(self, df):
        a = df['high_preadj'][-2745:] - df['low_preadj'][-2745:]
        a[abs(a) < 1e-8] = np.nan
        factor = df['volume_preadj'][-2745:] * ((df['close_preadj'][-2745:] - df['low_preadj'][-2745:]) - (df['high_preadj'][-2745:] - df['close_preadj'][-2745:])) / a
        factor = multi_processing_joblib(df=factor, func=ts_truncated_ema, n_jobs=-1, d=200, alpha= 1/45).values[-2545:]
        factor = bk.move_rank(factor, 1200, 600, axis = 0)[-1345:]
        factor = bk.move_mean(factor, 15, 7, axis = 0)[-1330:]

        factor = rolling_norm(factor, 5 * 242)[-120:]

        cr = (2 * df['stk_index_corr_zz500'].rank(axis=1, pct=True) - 1).values[-120:]
        factor = factor * cr
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 20, 10, axis = 0)[-100:]
        factor = np.nanmean(factor)

        return factor
##########
import numpy as np
from operators_wsc_1_0 import *
from future_factor import FutureFactor



class wyc_fast2_cfghf(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['amount', 'close', 'BuyUniqueOrderNum', 'SellUniqueOrderNum']
    normalize_size = 237 * 3
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False

    def calculate(self, data):
        stk_close = data['close'].values[-12:]
        stk_amount = data['amount'].values[-12:]
        stk_BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-12:]
        stk_SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-12:]
        
        order_num = stk_BuyUniqueOrderNum + stk_SellUniqueOrderNum
        ret = ts_pct_change(stk_close, 1)
        ret[ret > 0] = 0
        ret[ret < 0] = 1
        down_amount = stk_amount * ret
        down_ordernum = order_num * ret
        amount_per_order = ts_sum(np.nansum(stk_amount, axis=1), 10) / ts_sum(np.nansum(order_num, axis=1), 10)
        down_amount_per_order = ts_sum(np.nansum(down_amount, axis=1), 10) / ts_sum(np.nansum(down_ordernum, axis=1), 10)
        factor = amount_per_order / down_amount_per_order
        return factor[-1]
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:55:28 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class GA_ind_nr_w_a_CFG_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = [ 'amount', 'weight', 'close','low','high', 'open', 'adjfactor']
    #data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 242 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:09:05 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class ClMaxClMin_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close']} 
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    instrument_type='recent'
    
    def calculate(self, data):
        hclose = data['close_cont_IC'].iloc[-45:].values
        
        return np.nanmax(hclose)/np.nanmin(hclose)
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

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

class wyc_ts38_spot(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 5 * 242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 

    def calculate(self, df):
        
        close = df['close_000905.SH'][-1360:]
        temp1 = close.copy()
        condition = close > close.shift(1)
        closestd = close.rolling(20, min_periods = 10).std()
        temp1[condition] = closestd
        temp1[~condition] = 0
        a = ts_truncated_ema(temp1[-1340:], 5 * 242, 1/100).values[-130:]

        temp1[condition] = 0
        temp1[~condition] = closestd
        b = ts_truncated_ema(temp1[-1340:], 5 * 242, 1/100).values[-130:]

        c = a + b
        c[abs(c) < 1e-8] = np.nan
        factor = a / c * 100
        factor = bk.move_rank(factor, 30, 15, axis = 0)[-100:]
        factor = np.nanmean(factor)
        return factor

##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk

class wyc_if_2hour_return_ws_cfg(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = ['close','weight','adjfactor']
    normalize_size = 5 * 242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, df):
        cif = df['close_preadj'].values[-300:]
        cif[abs(cif) < 1e-8] = np.nan
        ifreturn = cif[1:] / cif[:-1] - 1
        factor = bk.move_mean(ifreturn, 200, min_count=100, axis = 0)

        factor = factor[-90:] * df['weight'].values[-90:]
        factor = np.nansum(factor,axis=1)

        factor = bk.move_rank(factor, 50, 25, axis = 0)
        factor = np.nanmean(factor[-40:])

        return factor
##########
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_cc import *
from future_factor import FutureFactor


def r(data, x=np.nan):

    data[abs(data) < 1e-8] = x
    return data

    
class Short_BS_Main_CFG_CC(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['amount', 'weight', 'BuyUniqueOrderNum', 'BuyTradeNum', 'SellUniqueOrderNum', 'SellTradeNum']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-13:]
        stk_weight = data['weight'].values[-13:]
        stk_BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-13:]
        stk_BuyTradeNum = data['BuyTradeNum'].values[-13:]
        stk_SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-13:]
        stk_SellTradeNum = data['SellTradeNum'].values[-13:]

        df_s = bk.move_sum(stk_amount, 10, 5, axis=0)
        df_s[stk_weight<=0] = np.nan
        amount_mask = np.nanquantile(df_s, 0.9, axis=1)
        amount_mask = np.expand_dims(amount_mask, axis=-1)
        factor_raw = (stk_BuyUniqueOrderNum / r(stk_BuyTradeNum)) - (stk_SellUniqueOrderNum / r(stk_SellTradeNum))
        factor_raw_after_mask = ma.array(factor_raw, mask=(df_s<=amount_mask))
        factor_raw_after_mask = np.nanmean(factor_raw_after_mask, axis=1)
        factor_mean = -bk.move_mean(factor_raw_after_mask, 3, 1)
        return factor_mean[-1]
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from future_factor import FutureFactor

class tr1_zf(FutureFactor):
    '''
    期货类因子
    '''
    data_type = 'Future' #'IndexStock'
    days_past = 2
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close','low','high']}
    normalize_size = 242 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'

    def calculate(self, data):
        high = data['high_000905.SH'].values
        high = high[-242:]
        hh = np.nanmax(high)
        low = data['low_000905.SH'].values
        low = low[-242:]
        ll = np.nanmin(low)
        return (2*data['close_000905.SH'].values[-1])/(hh+ll)
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:47:17 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

  
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
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

def get_norm(fa):
    fmax = np.nanmax(fa)
    fmin = np.nanmin(fa)
    divisor = fmax - fmin
    if divisor < 1e-8:
        divisior = np.nan
    return ((fa[-1] - fmin)/ divisor) * 2 - 1

class wyc_ts40_future(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close', 'vwap']}
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 
    
    def calculate(self, df):
        vwap = df['vwap_cont_IC'][-1410:]
        
        close_s20 = df['close_cont_IC'].shift(20)[-1410:]
        s = vwap.rolling(60, min_periods=30).std()
        f = close_s20.rolling(60, min_periods=30).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        aa = vwap.rolling(20, min_periods=10).cov(close_s20) / (s * f)
        
        close = df['close_cont_IC'][-1350:]
        ctemp = (bk.move_sum(close, 20, 10, axis = 0) / 20) - close
        
        factor = ctemp[-1330:] + aa[-1330:]
        factor = bk.move_rank(factor, 20, 10, axis = 0)[-1310:]
        factor = bk.move_mean(factor, 100, 50, axis = 0)[-1210:]
        factor = get_norm(factor)

        return factor
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc7_cfg_ar(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'close', 'high', 'low', 'adjfactor']
    normalize_size = 1800
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-110:]
        stk_high = data['high_preadj'].values[-110:]
        stk_low = data['low_preadj'].values[-110:]
        stk_amount = data['amount'].values[-110:]
        amount_rank_mask = section_rank_np(stk_amount, pct=True) * 2 - 1
        n = 20
        m = 60
        low_n = ts_min(stk_low, n)
        high_n = ts_max(stk_high, n)
        a = replace_zero(high_n - low_n)
        stochastics = (stk_close- low_n) / a
        stochastics_low = ts_min(stochastics, m)
        stochastics_high = ts_max(stochastics, m)
        c = replace_zero(stochastics_high - stochastics_low)
        stochastics_double = (stochastics - stochastics_low) / c
        factor_raw = np.nansum(stochastics_double * amount_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 30)
        return factor_mean[-1]

##########
import numpy as np
import pandas as pd
from help_functions_wsc import *
from future_factor import FutureFactor


def type_convertor(func):
    """
    与operators文件中的算子相配套，用于调整输出的数据格式，使之与输入的数据格式相一致
    """
    def wrapper(*args, **kwargs):
        data = args[0]
        if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
            raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
        output = func(*args, **kwargs)
        if isinstance(data, pd.DataFrame):
            output = pd.DataFrame(output, index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(output, index=data.index, name=data.name)
        return output
    return wrapper


@type_convertor
def ts_position(data, d):
    if not isinstance(data, np.ndarray):
        data = data.values
    data_expanding = rolling_window_upgrade(data, d)
    output_need = (data_expanding[...,-1] - np.nanmin(data_expanding, axis=-1)) / (np.nanmax(data_expanding, axis=-1) - np.nanmin(data_expanding, axis=-1))
    output = np.full(data.shape, np.nan)
    output[d - 1:] = output_need
    return output


class wyc_fast1_spot(FutureFactor):

    data_type = 'Future' 
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 237 * 3
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False

    def calculate(self, data):
        spot_close = data['close_000905.SH'].values[-50:]

        factor = ts_position(spot_close, 50)
        return factor[-1]
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

def rolling_norm(sig, window=1200, method='max_min'):
    assert isinstance(sig, pd.Series) or isinstance(sig, pd.DataFrame) or isinstance(sig, np.ndarray), 'input must be a series, dataframe or ndarray'
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
            elif isinstance(sig, np.ndarray):
                sig_max = bk.move_max(sig, window=window, min_count=int(window / 2), axis=0)
                sig_min = bk.move_min(sig, window=window, min_count=int(window / 2), axis=0)
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
            elif isinstance(sig, np.ndarray):
                output = bk.move_rank(sig, window=d, min_count=int(d / 2), axis=0)
            return signal

class wyc_if_2hour_return_nr_as_cfg(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['close','amount','adjfactor']
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, df):
        cif = df['close_preadj'].values
        cif[abs(cif) < 1e-8] = np.nan
        ifreturn = cif[1:] / cif[:-1] - 1
        factor = bk.move_mean(ifreturn, 200, min_count=100, axis = 0)

        factor = rolling_norm(factor, 5 * 242)

        a = df['amount'].values
        factor = factor * a[1:]
        factor = np.nansum(factor,axis = 1)

        factor = bk.move_rank(factor[-90:], 50, 25, axis = 0)
        factor = np.nanmean(factor[-40:])

        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:24:46 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


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
##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd
import scipy
from joblib import Parallel, delayed

def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    # 这是后面算子计算的辅助函数
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    return rolling_table

    
def get_top_mean(df1, d):
    output = pd.Series(np.nan, index=df1.index)
    a = rolling_window(df1, d)
    b = np.sort(a)
    c = np.nanmean(b[:,-5:], axis=1)
    flag = np.sum(np.isnan(a), axis=1) 
    flag = np.where(flag <= d - int(d / 2), 1, np.nan)
    output.iloc[d - 1:] = c * flag
    return output


def multi_processing(df, func, n_jobs, **kwargs):
    results = Parallel(n_jobs=n_jobs)(delayed(func)(df[i], **kwargs) for i in df.columns)
    results_df = pd.DataFrame(results, index=df.columns, columns=df.index)
    return results_df.T

class stk2idx_maxret_diff_chg_zsj(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close','adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        ## prep data
        stk_close = data['close_preadj'][-101:]
        stk_ret = stk_close / stk_close.shift(1) - 1

        stk_max_ret = multi_processing(df=stk_ret, func=get_top_mean, n_jobs=1, d=60)

        stk_ret_duration = stk_close/stk_close.shift(5) - 1 
        stk_maxret_diff = stk_max_ret - (stk_ret_duration/5)
        stk_maxret_diff[~np.isfinite(stk_maxret_diff)] = np.nan
        stk2idx_maxret_diff_raw = np.nanmean(stk_maxret_diff[-30:].values, axis=1)
        factor = np.nanmean(stk2idx_maxret_diff_raw[-10:]) - np.nanmean(stk2idx_maxret_diff_raw)  
        
        return factor
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc11_cfg_search_wr(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['weight', 'close', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-36:]
        stk_weight = data['weight'].iloc[-36:]
        weight_rank_mask = stk_weight.rank(axis=1, pct=True) * 2 - 1
        # weight_rank_mask = section_rank_np(stk_weight, pct=True) * 2 - 1
        factor_init = ts_max(ts_delta(stk_close, 15), 20)
        factor_raw = np.nansum(factor_init * weight_rank_mask.values, axis=1)
        return factor_raw[-1]

##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *


    
class wsc_hf19(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'PxStd', 'VolStd']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-15:]
        stk_PxStd = data['PxStd'].values[-15:]
        stk_VolStd = data['VolStd'].values[-15:]
        factor_init = pairwise_corr_np(ts_mean(stk_PxStd, 15)[-1], ts_mean(stk_VolStd, 15)[-1])
        factor_raw = -factor_init * ts_mean(np.nansum(stk_amount, axis=1), 15)[-1]
        return factor_raw
##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

class u2d_vol_ratio_zsj(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close','adjfactor','volume']
    normalize_size = 242*3
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        stk_close = data['close_preadj'][-91:]
        stk_volume = data['volume_preadj'][-90:]
        stk_ret = (stk_close / stk_close.shift(1) - 1)[-90:]
        up_mask = stk_ret > 0
        down_mask = stk_ret < 0

        up_vol = stk_volume[up_mask].sum(axis=1)
        down_vol = stk_volume[down_mask].sum(axis=1)
        down_vol[abs(down_vol)<1e-8] = np.nan
        u2d_vol_ratio_raw = up_vol / down_vol
        factor = np.nanmean(u2d_vol_ratio_raw)

        return factor
##########
import numpy as np
import bottleneck as bk
from operators_wsc_1_0 import *
from future_factor import FutureFactor


def section_rank_bk(data, pct=False):
    # numpy的argsort函数在值相同的情况下会出现排序不稳定的情况，所以用bk.rankdata代替，对应df.rank(method='first')
    if not isinstance(data, np.ndarray):
        raise TypeError('Only supports the following type: np.ndarray')
    data_argsort = bk.rankdata(data, axis=1)  # +1是因为numpy从0计数，pandas从1计数
    data_argsort[np.isnan(data)] = np.nan  # numpy argsort会让nan也参与排序，但是pandas不会，所以把这些值重新置为nan
    if pct == True:
        data_argsort = data_argsort / (~np.isnan(data)).sum(axis=1, keepdims=True)
    return data_argsort


class wsc_fast18_hf(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'BuyTradeMoney']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False

    def calculate(self, data):
        stk_close = data['close'].values[-17:]
        stk_BuyTradeMoney = data['BuyTradeMoney'].fillna(0).values[-17:]

        x = section_rank_bk(stk_BuyTradeMoney, pct=True) * 2 - 1
        stk_ret = ts_pct_change(stk_close, 1)
        factor_raw = np.nansum(x * stk_ret, axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        return factor_mean[-1]
##########
from future_factor import FutureFactor
from operators_wsc_1_0 import *


class wsc2_spot(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 380
    normalize_type = 'rolling_norm'
#    num_range = '[0,1]'
    
    def calculate(self, data):
        spot_close = data['close_000905.SH'].values[-85:]
        close_ma_long = ts_mean(spot_close, 85)
        close_ma_short = ts_mean(spot_close, 10)
        factor_raw = close_ma_short - close_ma_long
        return factor_raw[-1]
##########
import numpy as np
from operators_wsc_1_0 import *
from future_factor import FutureFactor


class wsc_fast1_cfg(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'weight', 'adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        spot_close = data['close_000905.SH'].values[-24:]
        stk_close = data['close_preadj'].values[-24:]
        stk_weight = data['weight'].values[-24:]

        spot_ret = ts_pct_change(spot_close, 20)
        stk_ret = ts_pct_change(stk_close, 20)
        excess_ret = sub2(stk_ret, spot_ret)
        stk_weight[excess_ret >= 0] = np.nan
        factor_raw = np.nansum(stk_weight, axis=1)
        factor_mean = ts_mean(factor_raw, 3)
        return factor_mean[-1]
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk

def get_norm(fa):
    fmax = np.nanmax(fa)
    fmin = np.nanmin(fa)
    divisor = fmax - fmin
    if divisor < 1e-8:
        divisior = np.nan
    return ((fa[-1] - fmin)/ divisor) * 2 - 1

def get_delta(data, n):
    return data[n:] - data[:-n]
    
class wyc_ts5_future(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 11
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close']} 
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.75,1]'
    handle_preadj = None 

    def calculate(self, df):
        N = 45
        close = df['close_cont_IC'].values
        origin = get_delta((bk.move_sum(close, N,int(N/2), axis =0) / N), N) / close[:-N]
        change1 = -1 * (close - bk.move_min(close, N,int(N/2), axis =0))[N:]
        change2 = -1 * get_delta(close, 3)[N-3:]
        factor = np.where(origin<=0.05,change1,change2)[-1200 - 15 - 5*242:]
        factor = bk.move_rank(-1*factor, 1200, 600, axis = 0)[-5*242 - 15:]
        factor = bk.move_mean(factor,15,7,axis = 0)

        factor = get_norm(factor[-5*242:])
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:34:38 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class ZHZH_ind_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['high']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '[0, 1]'
    
    def calculate(self, data):
        hhigh = (data['high_000905.SH'].values)[-80:]
        factor = bk.move_mean((hhigh>=bk.move_max(hhigh, 15, min_count = 5)).astype(int), 60, min_count = 5)
        
        return factor[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:06:11 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd



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
##########
import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import multi_processing_joblib
from operators_wsc_1_0 import *


class wsc_cfg9(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'weight', 'high', 'low', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'rolling_norm'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-125:]
        stk_high = data['high_preadj'].values[-125:]
        stk_low = data['low_preadj'].values[-125:]
        stk_weight = data['weight'].values[-125:]
        N = 30
        stk_close_ema = multi_processing_joblib(stk_close, ts_truncated_ema, n_jobs=-1, d=60, alpha=(N-1)/(N+1))
        bull_power = stk_high - stk_close_ema
        bear_power = stk_low - stk_close_ema
        factor_init = bull_power + bear_power
        factor_raw = np.nansum(factor_init * stk_weight, axis=1)
        factor_raw = -ts_mean(factor_raw, 65)
        return factor_raw[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:03:59 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class VLSM_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','amount', 'low', 'high','open', 'weight','volume', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.5, 1]'# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
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
        t = np.nanmean(t_pcorr*stk_amount)
        
        return t
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_cfg3(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'weight', 'adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-70:]
        stk_weight = data['weight'].values[-70:]
        spot_close = data['close_000905.SH'].values[-70:]
        stk_ret = ts_pct_change(stk_close, 60)
        index_ret = ts_pct_change(spot_close, 60)
        # print(index_ret)
        excess_ret = sub2(stk_ret, index_ret)
        # print(excess_ret)
        excess_ret[excess_ret>=0] = 0
        excess_ret[excess_ret<0] = 1
        #print(excess_ret.shape)
        factor_raw = np.nansum(excess_ret * stk_weight, axis=1)
        factor_raw = ts_mean(factor_raw, 10)
        #print(factor_raw.shape)
        return factor_raw[-1]
##########
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero


class wsc_ti19_spot(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        spot_close = data['close_000905.SH'].values[-206:]
        temp = replace_zero(ts_sum(abs(ts_delta(spot_close, 1)), 10))
        vi = abs(ts_delta(spot_close, 10)) / temp
        vidya = vi * spot_close + (1 - vi) * ts_delay(spot_close, 1)
        factor_init = spot_close - vidya
        factor_raw = ts_mean(factor_init, 180)
        return factor_raw[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:09:24 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd



class HDL_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['high', 'low']} 
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '(-0.5, 1]'
    instrument_type='recent'
    
    def calculate(self, data):
        
        hhigh = data['high_cont_IC'].iloc[-50:]
        hlow = data['low_cont_IC'].iloc[-50:]
        hdl_r = (bk.move_max(hhigh, 25, min_count = 10, axis = 0))/(bk.move_min(hlow, 25, min_count = 10, axis = 0))
        factor = np.nanmean(hdl_r[-10:])
        
        return factor
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_ts44_future_ws(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = ['close', 'volume', 'adjfactor', 'weight'] 
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, df):
        volume = df['volume_preadj'][-350:]
        close = df['close_preadj'][-350:]
        temp1 = volume.copy(deep = True)
        con2 = close < close.shift(1)
        temp1[con2] = -1 * volume
        
        factor = bk.move_sum(temp1, 20, 10, axis = 0)[-330:]
        factor = bk.move_mean(factor, 20, 10, axis = 0)[-310:]

        w = df['weight'][-310:].values
        factor = factor * w
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 300, 150, axis = 0)[-10:]
        factor = np.nanmean(factor)
        
        return factor
##########
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_cc import *
from future_factor import FutureFactor


def r(data, x=np.nan):

    data[abs(data) < 1e-8] = x
    return data

    
def section_rank_bk(data, pct=False):
    # numpy的argsort函数在值相同的情况下会出现排序不稳定的情况，所以用bk.rankdata代替，对应df.rank(method='first')
    if not isinstance(data, np.ndarray):
        raise TypeError('Only supports the following type: np.ndarray')
    data_argsort = bk.rankdata(data, axis=1)  # +1是因为numpy从0计数，pandas从1计数
    data_argsort[np.isnan(data)] = np.nan  # numpy argsort会让nan也参与排序，但是pandas不会，所以把这些值重新置为nan
    if pct == True:
        data_argsort = data_argsort / (~np.isnan(data)).sum(axis=1, keepdims=True)
    return data_argsort


class Short_SYXWR_ar_CFG_CC(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['amount', 'open', 'close', 'low', 'high', 'adjfactor']
    normalize_size = 1200 
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        stk_amount = data['amount'].values[-35:]
        stk_close = data['close_preadj'].values[-35:]
        stk_open = data['open_preadj'].values[-35:]
        stk_high = data['high_preadj'].values[-35:]
        stk_low = data['low_preadj'].values[-35:]
        
        stk_amount_rank = section_rank_bk(stk_amount, pct=True) * 2 - 1
        temp1 = np.where(stk_open > stk_close, stk_open, stk_close)
        t_pcor = (stk_high - temp1) / r(bk.move_mean(stk_high - temp1, 30, 15, axis=0))
        t_pcor2 = (stk_close - bk.move_min(stk_low, 30, 15, axis=0)) / r(bk.move_max(stk_high, 30, 15, axis=0) - bk.move_min(stk_low, 30, 15, axis=0))
        t_pcorr = (t_pcor2 - t_pcor)
        factor = np.nansum(t_pcorr * stk_amount_rank, axis=1)
        factor = bk.move_mean(factor, 5, 2)
        return factor[-1]
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

def get_norm(fa):
    fmax = np.nanmax(fa)
    fmin = np.nanmin(fa)
    divisor = fmax - fmin
    if divisor < 1e-8:
        divisior = np.nan
    return ((fa[-1] - fmin)/ divisor) * 2 - 1

class wyc_ts108_future(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['close']}
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.5,1]'
    handle_preadj = None 
    
    def calculate(self, df):
        close = df['close_cont_IF'][-1322:]
        c = close - close.shift(1)
        factor = np.where(c < 0, abs(c), 0)
        factor = bk.move_sum(factor, 12, 6, axis = 0)[-1310:]
        factor = bk.move_rank(factor, 20, 10, axis = 0)[-1290:]
        factor = bk.move_mean(factor, 80, 40, axis = 0)[-1210:]
        factor = get_norm(factor)
        return factor
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class xdy_ts1_spot_ar(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = ['close', 'high', 'amount', 'adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[-1,0.5]'
    handle_preadj = True
    
    def calculate(self, df):
        high = df['high_preadj'][-330:].values
        close = df['close_preadj'][-330:].values
        high[abs(high) < 1e-8] = np.nan
        gain_high_60 = (high[60:] / high[:-60] - 1)[-270:]
        h_c = close / high - 1
        a = bk.move_mean(h_c, 60, 30, axis = 0)[-270:]
        a[abs(a) < 1e-8] = np.nan
        factor = bk.move_sum(gain_high_60 / a, 10, 5, axis = 0)[-260:]
        factor = -1 * bk.move_mean(factor, 10, 5, axis = 0)[-250:]

        a = df['amount'][-250:]
        ar = (2 * a.rank(axis=1, pct=True) - 1).values
        factor = factor * ar
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 50, 25, axis = 0)[-200:]
        factor = np.nanmean(factor)

        return factor
##########
import numpy as np
from operators_wsc_1_0 import *
from future_factor import FutureFactor


class wsc_fast13_cfg(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['amount', 'close', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        stk_close = data['close_preadj'].values[-7:]
        stk_amount = data['amount'].values[-7:]
        
        price_diff = ts_delta(stk_close, 1)
        up_num = (price_diff >= 0).sum(axis=1)
        down_num = (price_diff < 0).sum(axis=1)
        up_amount = np.nansum(np.where(price_diff >= 0, stk_amount, 0), axis=1)
        down_amount = np.nansum(np.where(price_diff < 0, stk_amount, 0), axis=1)
        factor_raw = (up_num / down_num) / (up_amount / down_amount)
        factor_mean = -ts_mean(factor_raw, 5)
        return factor_mean[-1]
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:18:43 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class VwLs_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['amount','volume', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.5, 1]'# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
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
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero


class wsc_ti4_cfg(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'amount', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-37:]
        stk_amount = data['amount'].values[-37:]
        price_diff = ts_delta(stk_close, 1)
        up_num = np.nansum((price_diff>=0), axis=1)
        down_num = np.nansum((price_diff<0), axis=1)
        up_amount = stk_amount.copy()
        up_amount[price_diff<0] = 0
        up_amount = np.nansum(up_amount, axis=1)
        down_amount = stk_amount.copy()
        down_amount[price_diff>=0] = 0
        down_amount = np.nansum(down_amount, axis=1)
        factor_init = (up_num / replace_zero(down_num+0.)) / replace_zero(up_amount / replace_zero(down_amount))
        factor_raw = -ts_mean(factor_init, 35)
        return factor_raw[-1]

##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_inf



class wsc_hf9(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'weight', 'Bid1AmtMean', 'Ask1AmtMean']
    normalize_size = 500
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        stk_close = data['close'].values[-39:]
        stk_weight = data['weight'].values[-39:]
        stk_Bid1AmtMean = data['Bid1AmtMean'].values[-39:]
        stk_Ask1AmtMean = data['Ask1AmtMean'].values[-39:]
        stk_ret = replace_inf(ts_pct_change(stk_close, 20))
        flag1 = (stk_Bid1AmtMean >= stk_Ask1AmtMean)
        flag2 = (stk_ret >= 0)
        factor_init = np.nansum(ts_sum(flag1*flag2, 10)*stk_weight, axis=1)
        factor_raw = ts_mean(factor_init, 9)
        return factor_raw[-1]
##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

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
    assert 0 < alpha < 1
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

class wsc5_spot(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 5
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low']}    
    normalize_size = 900
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    handle_preadj = None 
    
    def calculate(self, data):
        close = data['close_000905.SH']
        high = data['high_000905.SH']
        low = data['low_000905.SH']
        N = 30
        bull_power = high - ts_truncated_ema(close,1000, alpha=(N-1)/(N+1))
        bear_power = low - ts_truncated_ema(close,1000, alpha=(N-1)/(N+1))
        factor = bull_power + bear_power
        factor = np.nanmean(-1 * factor[-180:])
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:52:20 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class CFG23_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 10
    data_dict = dict()
    data_dict['Stock'] = ['close', 'adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[0, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:49:01 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

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

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:59:16 2021

@author: appadmin
"""


import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class HL123_CFG2_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['amount','high', 'low','adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.5, 1]'# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
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
##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

class wyc_ts102_spot(FutureFactor):

    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close','volume']}
    normalize_size = 1210
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    handle_preadj = None 
    
    def calculate(self, df):
        v = df['volume_000300.SH'][-17:].values
        c = df['close_000300.SH'][-17:].values
        v_delta = v[5:] - v[:-5]
        c_delta = c[5:] - c[:-5]
        a = -1 * np.sign(v_delta) * c_delta
        factor = bk.move_mean(a, 2, min_count=1, axis= 0)[-10:]
        factor = np.nanmean(factor)
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:24:10 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class L123_CC(FutureFactor):

    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['low']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '[0, 1]'
    instrument_type='recent'
    
    def calculate(self, data):

        hlow = (data['low_cont_IC'].values)[-90:]
        i11 = bk.move_min(hlow, 10, min_count = 5) - bk.move_min(hlow, 25, min_count = 10)
        i12 = bk.move_min(hlow, 20, min_count = 15) - bk.move_min(hlow, 30, min_count = 10)
        i2 = bk.move_mean((i11-i12), 30, min_count = 2)

        
        return i2[-1]
##########
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import *



class ret_a2p_sharpe_zsj(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'close', 'adjfactor']
    normalize_size = 2400
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-42:]
        stk_close = data['close_preadj'].values[-42:]
        stk_ret = ts_pct_change(stk_close, 1)
        cut_line = np.nanmedian(stk_amount, axis=1, keepdims=True)
        active_raw = ma.array(stk_ret, mask=(stk_amount<cut_line))
        inactive_raw = ma.array(stk_ret, mask=(stk_amount>=cut_line))
        active_raw = np.nanmean(active_raw, axis=1)
        inactive_raw = np.nanmean(inactive_raw, axis=1)
        a = ts_std(active_raw, 10)
        b = ts_std(inactive_raw, 10)
        ret_active_sharpe_raw = ts_mean(active_raw, 10) / replace_zero(a)
        ret_inactive_sharpe_raw = ts_mean(inactive_raw, 10) / replace_zero(b)
        ret_a2p_sharpe_raw = ret_active_sharpe_raw - ret_inactive_sharpe_raw
        factor_raw = ts_mean(ret_a2p_sharpe_raw, 30)
        return factor_raw[-1]



##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:26:23 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class LminLmean_IFIC_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':[ 'low']}
    normalize_size = 242*3
    normalize_type = 'ts_rank'
    instrument_type='recent'
    #num_range = [-0.499999, 1]
    
    def calculate(self, data):


        low = data['low_cont_IF'].values[-60:]
        temp1 = np.nanmin(low)
        temp2 = np.nanmean(low[-30:])
        factor = -temp1/temp2
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:22:08 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


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
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd
        
class wyc_ts414_cr_cfg(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'stk_index_corr_zz500', 'adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, df):
        close = df['close_preadj'][-80:]
        factor = np.where(close > close.shift(2), close.rolling(50, min_periods = 25).std(), 0)

        factor = np.nanmean(factor[-30:], axis = 0)
        s = 2 * df['stk_index_corr_zz500'][-1:].rank(axis = 1, pct=True) - 1
        factor = factor * s
        factor = np.nansum(factor, axis=1)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:33:48 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class SmaxSmean_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['share']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '(-0.5, 1]'
    instrument_type='recent'
    
    def calculate(self, data):
        hshare = (data['share_cont_IC'].values)[-120:]
        
        a = np.nanmean(hshare[-30:])
        b = np.nanmean(hshare)
        factor = a-b
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:06:35 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class GA_ind_IFIC_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close', 'high', 'low', 'open']} 
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
#    num_range = '(-0.5, 1]'
    
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
##########
from future_factor import FutureFactor
import numpy as np


class wyc_bigon_cfghf(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum','BuyTradeNum']
    normalize_size = 5 * 242 
    normalize_type = 'ts_rank' 
    num_range = None 
    handle_preadj = None
  

    def calculate(self, df):
        
        btn = df['BuyTradeNum'].values[-14:]
        btn[abs(btn) < 1e-8] = np.nan
        factor = 1 - df['BuyUniqueOrderNum'].values[-14:] / btn

        factor = np.nansum(factor, axis =1)
        factor = np.nanmean(factor)
        return factor
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero


class wsc_hf1(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['BuyTradeNum', 'weight', 'BuyUniqueOrderNum']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        stk_BuyTradeNum = replace_zero(data['BuyTradeNum'].values[-25:])
        stk_BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-25:]
        stk_weight = data['weight'].values[-25:]
        factor_init = np.nansum(stk_BuyUniqueOrderNum * stk_weight / stk_BuyTradeNum, axis=1)
        factor_raw = -ts_mean(factor_init, 25)
        return factor_raw[-1]
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:04:36 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

    
class ClMaxClMin_IFIC_CC(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['close']} 
    normalize_size = 3 * 240
    normalize_type = 'ts_rank'
    instrument_type='recent'
    
    def calculate(self, data):
        
        hclose = data['close_cont_IF'].values[-30:]
        
        factor = np.nanmax(hclose)/np.nanmin(hclose)

        
        return factor
##########
from future_factor import FutureFactor
from operators_wsc_1_0 import *


class wsc_mean_plus_std(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 600
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        spot_close = data['close_000905.SH'].values[-45:]
        spot_ret = ts_pct_change(spot_close, 5)
        close_mean = ts_mean(spot_ret, 30)
        close_std = ts_std(spot_ret, 30)
        factor_init = close_mean + 2 * close_std
        factor_raw = ts_mean(factor_init, 10)
        return factor_raw[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:33:27 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class SYXWR_ind_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':[ 'high', 'low', 'close', 'open']}
    instrument_type='recent'
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

        
        return np.nanmean((t_pcor2 - t_pcor)[-90:])
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:51:58 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class CFG23_2_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'adjfactor', 'amount']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[-0.5, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:25:11 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


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
    
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

def get_norm(fa):
    fmax = np.nanmax(fa)
    fmin = np.nanmin(fa)
    divisor = fmax - fmin
    if divisor < 1e-8:
        divisior = np.nan
    return ((fa[-1] - fmin)/ divisor) * 2 - 1

class wyc_ts208_future(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IH':['close']}
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.5,1]'
    handle_preadj = None 
    
    def calculate(self, df):
        close = df['close_cont_IH'][-1342:]
        c = close - close.shift(1)
        factor = np.where(c < 0, abs(c), 0)
        factor = bk.move_sum(factor, 12, 6, axis = 0)[-1330:]
        factor = bk.move_rank(factor, 20, 10, axis = 0)[-1310:]
        factor = bk.move_mean(factor, 100, 40, axis = 0)[-1210:]
        factor = get_norm(factor)
        return factor
##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

class VwRetSk_CC(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['vwap']}
    normalize_size = 1200
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    handle_preadj = None 
    
    def calculate(self, data):
        vsk_r = data['vwap_cont_IC'][-31:].diff()
        factor = -1 * vsk_r.rolling(30, min_periods = 15).skew().values[-1]       
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:53:09 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

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
##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd
import datetime
 
class wsc_cfg7(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'adjfactor', 'weight']
    normalize_size = 500 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        # 长短期收益率之差
        stk_close = data['close_preadj'][-121:]
        stk_ret_short = stk_close.pct_change(15, fill_method=None)
        stk_ret_long = stk_close.pct_change(120, fill_method=None) 
        a = stk_ret_long - stk_ret_short
        a[a<0] = 0
        factor = np.nansum((a[-1:] * data['weight'][-1:]).values,axis = 1)      
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:08:39 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

    
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

        return factor   

##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_ts14_future_cr(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = ['close','adjfactor','stk_index_corr_zz500'] 
    normalize_size = 5 * 242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True 

    def calculate(self, df):
        close = df['close_preadj'][-390:]
        factor = np.where(close > close.shift(2), close.rolling(50, min_periods=25).std(), 0)[-340:]
        factor = bk.move_mean(factor, 30, 15, axis = 0)[-310:]
        
        cr = (2 * df['stk_index_corr_zz500'][-310:].rank(axis=1, pct=True) - 1).values
        factor = factor * cr
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 300, 150, axis = 0)[-10:]
        factor = np.nanmean(factor)

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:24:26 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd



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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:06:51 2021

@author: appadmin
"""


import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


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
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd
from joblib import Parallel, delayed

def rolling_norm(sig, window=1200, method='max_min'):
    assert isinstance(sig, pd.Series) or isinstance(sig, pd.DataFrame) or isinstance(sig, np.ndarray), 'input must be a series, dataframe or ndarray'
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
            elif isinstance(sig, np.ndarray):
                sig_max = bk.move_max(sig, window=window, min_count=int(window / 2), axis=0)
                sig_min = bk.move_min(sig, window=window, min_count=int(window / 2), axis=0)
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
            elif isinstance(sig, np.ndarray):
                output = bk.move_rank(sig, window=d, min_count=int(d / 2), axis=0)
            return signal
        
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

class xdy_ts15_future_nr_as(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 8
    data_dict = dict()
    data_dict['Stock'] = ['high','amount','adjfactor']
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[-1,0]'
    handle_preadj = True
    
    def calculate(self, df):
        high = df['high_preadj'][-1830:]
        high = multi_processing_joblib(df=high, func=ts_truncated_ema, n_jobs=-1, d=200, alpha= 1/11)[-1630:]
        
        factor = bk.move_rank(high, 80, 40, axis = 0)[-1570:]
        factor = bk.move_mean(factor, 50, 25, axis = 0)[-1520:]

        factor = rolling_norm(factor, 5 * 242)[-310:]

        a = df['amount'][-310:].values
        factor = factor * a
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 300, 150, axis = 0)[-10:]
        factor = np.nanmean(factor)

        return factor
        
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:03:20 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


#
class SYXWR_ar_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'low', 'high','open', 'amount', 'adjfactor']
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
##########
import bottleneck as bk
import numpy as np
from future_factor import FutureFactor

class tr1_cfg_zf_cr(FutureFactor):
    '''
    成分股因子
    '''
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 3
    data_dict = dict()
    data_dict['Stock'] = ['close','high','low','adjfactor','stk_index_corr_zz500']
    normalize_size = 242*5 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        high = data['high_preadj'].values[-242*2-30:]
        low = data['low_preadj'].values[-242*2-30:]
        close = data['close_preadj'].values[-242*2-30:]
        hh = bk.move_max(high,window = 242, min_count = 30,axis=0)
        ll = bk.move_min(low, window = 242, min_count = 30,axis=0)
        facorg = 2*close/(hh+ll)
        fac_max = bk.move_max(facorg, window = 242, min_count = 121, axis=0)
        fac_min = bk.move_min(facorg, window = 242, min_count = 121, axis=0)
        tmp = fac_max-fac_min
        tmp[np.abs(tmp)<1e-8]=np.nan
        facorg = (facorg-fac_min)/tmp*2-1
        cr = (data['stk_index_corr_zz500'].iloc[-5:].rank(axis=1,pct=True))*2-1
        crr = cr.values
        fac = np.nansum(facorg[-5:]*crr,axis=1)
        return np.nanmean(fac)
##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

def get_norm(fa):
    fmax = np.nanmax(fa)
    fmin = np.nanmin(fa)
    divisor = fmax - fmin
    if divisor < 1e-8:
        divisior = np.nan
    return ((fa[-1] - fmin)/ divisor) * 2 - 1

class ts24_futures_zf(FutureFactor):

    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close','high','low']} 
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    handle_preadj = None 
    
    def calculate(self, data):
        N = 20
        wmadf = bk.move_mean(data['close_cont_IC'][-1350:].values, N, min_count=N//2, axis = 0)
        longc = bk.move_max(data['high_cont_IC'][-1350:].values, N, min_count=N//2, axis = 0) - wmadf
        shortc = bk.move_min(data['low_cont_IC'][-1350:].values, N, min_count=N//2) - wmadf
        factor =  ((longc - shortc) / data['close_cont_IC'][-1350:].values)[-1330:]
        factor = bk.move_rank(factor, 80, min_count=40, axis = 0)[-1250:]
        factor = bk.move_mean(factor, 40, min_count=20, axis = 0)[-1210:]
        factor = get_norm(factor)
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:34:11 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class ZHZH_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['high']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '(-0.5, 1]'
    instrument_type='recent'
    
    def calculate(self, data):
        hhigh = (data['high_cont_IC'].values)[-110:]
        factor = bk.move_mean((hhigh>=bk.move_max(hhigh, 10, min_count = 5)).astype(int), 90, min_count = 5)
        
        return factor[-1]
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

def get_norm(fa):
    fmax = np.nanmax(fa)
    fmin = np.nanmin(fa)
    divisor = fmax - fmin
    if divisor < 1e-8:
        divisior = np.nan
    return ((fa[-1] - fmin)/ divisor) * 2 - 1

class wyc_ts49_future(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close']}
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 
    

    def calculate(self, df):
        close = df['close_cont_IC'][-1560:]
        csum = bk.move_sum(close, 100, 50, axis = 0) / 100
        con1 = ((csum[100:] - csum[:-100]) / close.shift(100)[100:]) <= 0.05
        
        temp1 = close[100:].copy(deep = True)
        temp1[con1] = close - bk.move_min(close, 200, 100, axis = 0)
        temp1[~con1] = close - close.shift(10)
        
        factor = bk.move_rank(temp1, 50, 25, axis = 0)[-1260:]
        factor = bk.move_mean(factor, 50, 25, axis = 0)[-1210:]
        factor = get_norm(factor)
        
        return factor

##########
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_cc import *
from future_factor import FutureFactor


def r(data, x=np.nan):

    data[abs(data) < 1e-8] = x
    return data

    
class Short_BS_11_CC(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = ['amount', 'close', 'open', 'PxVolCorr', 'AbsPxPath']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-334:]
        stk_close = data['close'].values[-334:]
        stk_open = data['open'].values[-334:]
        stk_PxVolCorr = data['PxVolCorr'].values[-334:]
        stk_AbsPxPath = data['AbsPxPath'].values[-334:]

        df_s = bk.move_sum(stk_amount, 30, 15, axis=0)
        amount_mask = np.nanquantile(df_s, 0.9, axis=1)
        amount_mask = np.expand_dims(amount_mask, axis=-1)
        sig1 = ma.array(stk_PxVolCorr, mask=(df_s<=amount_mask))
        sig1 = np.nanmean(sig1, axis=1)
        sig1 = bk.move_rank(sig1, 300, 150)
        sig2 = ma.array((stk_close - stk_open) / r(stk_AbsPxPath), mask=(df_s<=amount_mask))
        sig2 = np.nanmean(sig2, axis=1)
        sig2 = bk.move_rank(sig2, 300, 150)
        sig = sig1 + sig2
        factor_mean = bk.move_mean(sig, 4, 2)
        return factor_mean[-1]
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *


    
class wsc_hf15(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['weight', 'PxVolCorr']
    normalize_size = 1800
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        stk_weight = data['weight'].values[-20:]
        stk_PxVolCorr = data['PxVolCorr'].values[-20:]
        factor_init = np.nansum(stk_weight*stk_PxVolCorr, axis=1)
        factor_raw = ts_mean(factor_init, 20)
        return factor_raw[-1]
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc8_cfg_ar(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'high', 'low', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_high = data['high_preadj'].values[-42:]
        stk_low = data['low_preadj'].values[-42:]
        stk_amount = data['amount'].values[-42:]
        amount_rank_mask = section_rank_np(stk_amount, pct=True) * 2 - 1
        n = 30
        hl = stk_high + stk_low
        high_abs = abs(ts_delta(stk_high, 1))
        low_abs = abs(ts_delta(stk_low, 1))
        dmz = np.maximum(high_abs, low_abs)
        dmz[ts_delta(hl, 1)<=0] = 0
        dmf = np.maximum(high_abs, low_abs)
        dmf[ts_delta(hl, 1)>=0] = 0
        a = replace_zero(ts_sum(dmz, n) + ts_sum(dmf, n))
        ddi = (ts_sum(dmz, n) - ts_sum(dmf, n)) / a
        factor_raw = np.nansum(ddi * amount_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 10)
        return factor_mean[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:08:12 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class vwap_ma_zsj(FutureFactor):
    
    data_type = 'Future'
    days_past = 6
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['high','low', 'close', 'volume']} 
    normalize_size = 0
    normalize_type = 'ts_rank'
#    num_range = '[0, 1]'
    instrument_type='recent'
    
    def calculate(self, data):
        close = data['close_cont_IC'].iloc[-1300:]
        high = data['high_cont_IC'].iloc[-1300:]
        low = data['low_cont_IC'].iloc[-1300:]
        volume = data['volume_cont_IC'].iloc[-1300:]

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
        factor = bk.move_mean(score_raw, 60, min_count = 54, axis = 0)
        factor = bk.move_rank(factor, 1200, min_count = 1080, axis = 0)[-1]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:06:12 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class CloseVoltoMean_ind_CC(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']} 
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
#    num_range = '(-0.2, 1]'
    
    def calculate(self, data):
        
        hclose = (data['close_000905.SH'].values)[-40:]
        return np.nanstd(hclose)/np.nanmean(hclose)



##########
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_gp8_future(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    # data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Continuous_Data'] = {'IC':['amount']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        future_amount = data['amount_cont_IC'].iloc[-105:]
        amount_std = ts_std(future_amount, 68)
        factor_raw = ts_reg_beta(amount_std, 37)
        return factor_raw[-1]
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 15:20:23 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

    
class HcorrC_ind_IFIC_CC(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['high', 'close']}
    normalize_size = 2420
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        hclose = (data['close_000300.SH']).iloc[-60:]
        hhigh = (data['high_000300.SH']).iloc[-60:]
        factor = hclose.corr(hhigh)
        return factor
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc10_cfg_vs(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'stk_volatility', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-131:]
        # print(stk_close.shape)
        stk_volatility = data['stk_volatility'].values[-131:]
        stk_ret_long = ts_pct_change(stk_close, 130)
        stk_ret_short = ts_pct_change(stk_close, 10)
        factor_init = stk_ret_long - stk_ret_short
        factor_init[factor_init < 0] = 0
        factor_raw = np.nansum(factor_init[-1] * stk_volatility[-1])
        return factor_raw

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:02:16 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


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
##########
import numpy as np
import bottleneck as bk
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


def section_rank_bk(data, pct=False):
    # numpy的argsort函数在值相同的情况下会出现排序不稳定的情况，所以用bk.rankdata代替，对应df.rank(method='first')
    if not isinstance(data, np.ndarray):
        raise TypeError('Only supports the following type: np.ndarray')
    data_argsort = bk.rankdata(data, axis=1)  # +1是因为numpy从0计数，pandas从1计数
    data_argsort[np.isnan(data)] = np.nan  # numpy argsort会让nan也参与排序，但是pandas不会，所以把这些值重新置为nan
    if pct == True:
        data_argsort = data_argsort / (~np.isnan(data)).sum(axis=1, keepdims=True)
    return data_argsort


class wsc_fast22_cfg(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'stk_index_corr_zz500', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-102:]
        stk_index_corr = data['stk_index_corr_zz500'].values[-102:]
        stk_index_corr_rank_mask = section_rank_bk(stk_index_corr, pct=True) * 2 - 1

        n = 10
        temp = replace_zero(ts_sum(abs(ts_delta(stk_close, 1)), n))
        vi = abs(ts_delta(stk_close, n)) / temp
        vidya = vi * stk_close + (1-vi) * ts_delay(stk_close, 1)
        factor_init = rolling_norm(vidya, 90)
        factor_raw = np.nansum(factor_init * stk_index_corr_rank_mask, axis=1)
        return factor_raw[-1]
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 10:13:32 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from operators_cc import *
import pandas as pd

class CloseVoltoMean_cr_CFG_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [ 'volume', 'close', 'adjfactor', 'stk_index_corr_zz500']
    #data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 720 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):

        stk_index_corr = data['stk_index_corr_zz500'].iloc[-61:]
        
        mask = (2 * stk_index_corr.rank(axis=1, pct=True) - 1).values
        
        stk_close = data['close_preadj'].iloc[-61:]
        
        prstd3_r = bk.move_std(stk_close, 40, min_count = 5, axis = 0)/bk.move_mean(stk_close, 40, min_count = 5, axis = 0)
        
        factor = np.nansum((prstd3_r*mask), axis = 1)
        factor = np.nanmean(factor[-20:])

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 10:15:11 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from operators_cc import *
import pandas as pd

class hhll_ind_CC_nr_ct_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
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
        
        mask = (tempp2 * tempp4)
        factor = np.nansum(factor1*mask, axis = 1)
        
        factor = np.nanmean(factor[-30:])
        return factor
##########
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import *


class trade_strength_a2p_zsj(FutureFactor):
    data_type = 'IndexStock'
    days_past = 21
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'close', 'adjfactor']
    normalize_size = 800
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-4861:]
        stk_close = data['close_preadj'].values[-4861:]
        roll_win = 30
        min_pct = 0.9        
        min_periods = int(min_pct * roll_win)
        ma_win = 30
        ts_pct_win = 4800
        cut_line = np.nanmedian(stk_amount, axis=1, keepdims=True)
        abs_dis = np.abs(ts_delta(stk_close, 1))
        stk_tot_dis = bk.move_sum(abs_dis, roll_win, min_periods, axis=0)
        stk_final_dis = ts_delta(stk_close, roll_win)
        stk_trade_strength = stk_final_dis / replace_zero(stk_tot_dis)
        ts_active_raw = ma.array(stk_trade_strength, mask=(stk_amount<cut_line))
        ts_inactive_raw = ma.array(stk_trade_strength, mask=(stk_amount>=cut_line))
        ts_a2p_raw = np.nanmean(ts_active_raw, axis=1) - np.nanmean(ts_inactive_raw, axis=1)
        ts_pct_np = bk.move_mean(ts_a2p_raw, ma_win, int(ma_win*min_pct), axis=0)
        factor_raw = bk.move_rank(ts_pct_np, ts_pct_win, int(ts_pct_win*min_pct), axis=0)
        return factor_raw[-1]

##########
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero


class wsc_ti2_spot(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'amount']}
    normalize_size = 950
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        spot_close = data['close_000905.SH'].values[-60:]
        spot_high = data['high_000905.SH'].values[-60:]
        spot_low = data['low_000905.SH'].values[-60:]
        spot_amount = data['amount_000905.SH'].values[-60:]
        x = replace_zero(spot_high - spot_low)
        amount_adj = (2 * spot_close - spot_high - spot_low) / x * spot_amount
        factor_raw = ts_sum(amount_adj, 60)
        return factor_raw[-1]

##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

def rolling_norm(sig, window=1200, method='max_min'):
    assert isinstance(sig, pd.Series) or isinstance(sig, pd.DataFrame) or isinstance(sig, np.ndarray), 'input must be a series, dataframe or ndarray'
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
            elif isinstance(sig, np.ndarray):
                sig_max = bk.move_max(sig, window=window, min_count=int(window / 2), axis=0)
                sig_min = bk.move_min(sig, window=window, min_count=int(window / 2), axis=0)
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
            elif isinstance(sig, np.ndarray):
                output = bk.move_rank(sig, window=d, min_count=int(d / 2), axis=0)
            return signal
        
        
class xdy_ts6_spot_nr_ts(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 8
    data_dict = dict()
    data_dict['Stock'] = ['close','turnover_rate','adjfactor']
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[-1,0.2]'
    handle_preadj = True
    
    def calculate(self, df):
        close = df['close_preadj'][-1590:].values
        gain_close_30 = close[30:]/close[:-30] - 1
        factor = 2 * gain_close_30[20:] - gain_close_30[:-20]
        factor = bk.move_mean(factor, 110, 55, axis = 0)[-1430:]
        
        factor = rolling_norm(factor, 5 * 242)[-220:]

        t = df['turnover_rate'][-220:].values
        factor = factor * t
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 20, 10, axis = 0)[-200:]
        factor = np.nanmean(factor)

        return factor

##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_ts34_future_ts_50_100(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = ['close', 'turnover_rate', 'high', 'low', 'volume', 'adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[0,1]'
    handle_preadj = True 

    def calculate(self, df):
        high = df['high_preadj'][-300:].values
        low = df['low_preadj'][-300:].values
        close = df['close_preadj'][-300:].values
        volume = df['volume_preadj'][-300:].values
        chl = high - low
        chl[abs(chl) < 1e-6] = np.nan
        factor = ((close - low)-(high - close))/ chl * volume
        factor = bk.move_mean(factor, 150, 75, axis = 0)[-150:]

        t = df['turnover_rate'][-150:].values
        factor = factor * t
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 50, 25, axis = 0)[-100:]
        factor = np.nanmean(factor)
        return factor
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc4_cfg_cr(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'stk_index_corr_zz500', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '(-0.9,1]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-47:]
        stk_index_corr = data['stk_index_corr_zz500'].values[-47:]
        stk_index_corr_rank_mask = 2 * section_rank_np(stk_index_corr, pct=True) - 1
        N = 20
        dpo = stk_close - ts_delay(ts_mean(stk_close, N), int(N/2+1))
        factor_raw = np.nansum(dpo * stk_index_corr_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        return factor_mean[-1]

##########
import numpy as np
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


class wsc_fast9_spot(FutureFactor):

    data_type = 'Future' 
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    
    def calculate(self, data):
        spot_close = data['close_000905.SH'].values[-64:]
        
        n = 10
        temp = replace_zero(ts_sum(abs(ts_delta(spot_close, 1)), n))
        vi = abs(ts_delta(spot_close, n)) / temp
        vidya = vi * spot_close + (1 - vi) * ts_delay(spot_close, 1)
        factor_raw = spot_close - vidya
        factor_mean = ts_mean(factor_raw, 50)
        return factor_mean[-1]
##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd
import datetime
 
class wyc_ts414_ws_cfg(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'adjfactor', 'weight']
    normalize_size = 5 * 242 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, df):
        c = df['close_preadj'][-32:].values
        s = df['close_preadj'].rolling(30, min_periods = 15).std()[-32:].values
        
        factor = np.where(c[2:] > c[:-2], s[2:], 0)

        factor = factor[-30:] * df['weight'][-30:].values
        factor = np.nansum(factor, axis = 1)[-30:]
        factor = np.nanmean(factor)
      
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:54:50 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class DJC_cv_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 6
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
        
        hclose = stk_close.iloc[-290:]
        temp5 = bk.move_mean(hclose.iloc[-40:], 5, min_count = 2, axis = 0)
        temp10 = bk.move_mean(hclose.iloc[-40:], 10, min_count = 5, axis = 0)
        temp20 = bk.move_mean(hclose.iloc[-55:], 20, min_count = 10, axis = 0)
        temp60 = bk.move_mean(hclose.iloc[-105:], 60, min_count = 20, axis = 0)
        temp120 = bk.move_mean(hclose.iloc[-205:], 120, min_count = 60, axis = 0)
        
        temp5_diff = ((temp5[1:]-temp5[:-1]>1e-8).astype(int))[-26:]
        temp10_diff = ((temp10[1:]-temp10[:-1]>1e-8).astype(int))[-26:]
        temp20_diff = ((temp20[1:]-temp20[:-1]>1e-8).astype(int))[-26:]
        temp60_diff = ((temp60[1:]-temp60[:-1]>1e-8).astype(int))[-26:]
        temp120_diff = ((temp120[1:]-temp120[:-1]>1e-8).astype(int))[-26:]
        
        temp = (bk.move_mean((temp5_diff+temp10_diff+temp20_diff+temp60_diff+temp120_diff), 20, min_count = 15, axis = 0))[-5:]
        mask = (tempp2 * tempp3).values
        factor = np.nansum((temp*mask), axis = 1)
        factor = np.nanmean(factor)
        
        return factor
##########
import bottleneck as bk
import numpy as np
from future_factor import FutureFactor

class sr1_zf(FutureFactor):
	'''
	期货类因子
	'''
	data_type = 'Future'
	days_past = 3
	data_dict = dict()
	data_dict['Index_Id'] = {'000905.SH':['close','low']}
	normalize_size = 0 # normalize所用历史数据长度
	normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#	num_range = '(-0.5,1]'

	def calculate(self, data):
		close = data['close_000905.SH'].values
		rtn = close[1:]/close[:-1]-1
		vol_ts = bk.move_std(rtn,window = 60, min_count = 30, ddof = 1)
		vol_ts[abs(vol_ts)<1e-8] = np.nan
		low = data['low_000905.SH'].values
		low = low[:-1]
		lowmin = bk.move_min(low, window = 60, min_count = 30)
		ret = close[1:]/lowmin-1
		sig = ret/vol_ts
		sig = bk.move_rank(sig, window = 242*2, min_count = 242)[-5:]
		sig = np.nanmean(sig)
		return sig
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc11_cfg_search_cr(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['stk_index_corr_zz500', 'close', 'adjfactor']
    normalize_size = 1800
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-46:]
        stk_index_corr_zz500 = data['stk_index_corr_zz500'].values[-46:]
        stk_index_corr_rank_mask = section_rank_np(stk_index_corr_zz500, pct=True) * 2 - 1
        factor_init = ts_max(ts_delta(stk_close, 15), 15)
        factor_raw = np.nansum(factor_init * stk_index_corr_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        return factor_mean[-1]

##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero, replace_inf



class wsc3_cfg_ar(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Stock'] = ['close', 'amount', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].iloc[-113:]
        stk_amount = data['amount'].values[-113:]
        spot_close = data['close_000905.SH'].iloc[-113:]
        amount_rank_mask = 2 * section_rank_np(stk_amount, pct=True) - 1
        spot_ret = ts_pct_change(spot_close, 3)
        stk_ret = ts_pct_change(stk_close, 3)
        ret_diff = stk_ret.sub(spot_ret.iloc[:,0], axis=0)
        ret_diff[ret_diff > 0] = 1
        ret_diff[ret_diff <= 0] = 0
        ret_diff = ret_diff.values
        temp = replace_zero(ts_sum(ret_diff, 90))
        factor_init = replace_inf(ts_sum(ret_diff, 15) / temp)
        factor_raw = np.nansum(factor_init * amount_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 20)
        return factor_mean[-1]

##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd
import datetime

class wsc17_cfg_ret_as(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'adjfactor', 'amount']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        # 长江金工高频因子八，偏度因子
        # 计算close的偏度，偏度＞0时，大于价格均值的价格比小于价格均值的价格少，个股成交集中在价格相对较低的水平，反之亦然，因此认为偏度越小的股票未来价格更可能上升。
        # 取当分钟rolling_skew前50%的股票，计算它们的过去一分钟return，作为因子值，再套相应的mask，因为每期选出的票都不一样，所以为了时序上可比，要做一定的归一化处理。
        stk_close = data['close_preadj'][-75:]
        stk_amount = data['amount'][-45:]
        stk_ret = stk_close.pct_change()
        stk_skew = stk_close.rolling(30, min_periods=15).skew()
        skew_long = stk_skew.gt(stk_skew.quantile(0.5, axis=1), axis=0)
        factor_init = stk_ret[skew_long]

        factor_raw = (factor_init[-45:] * stk_amount).sum(axis=1).values / (stk_amount * skew_long[-45:]).sum(axis=1).replace(0, np.nan).values
        factor = np.nanmean(factor_raw)
     
        return factor
##########
import numpy as np
import bottleneck as bk
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


def section_rank_bk(data, pct=False):
    # numpy的argsort函数在值相同的情况下会出现排序不稳定的情况，所以用bk.rankdata代替，对应df.rank(method='first')
    if not isinstance(data, np.ndarray):
        raise TypeError('Only supports the following type: np.ndarray')
    data_argsort = bk.rankdata(data, axis=1)  # +1是因为numpy从0计数，pandas从1计数
    data_argsort[np.isnan(data)] = np.nan  # numpy argsort会让nan也参与排序，但是pandas不会，所以把这些值重新置为nan
    if pct == True:
        data_argsort = data_argsort / (~np.isnan(data)).sum(axis=1, keepdims=True)
    return data_argsort


class Short_tr1_cfg_zf_cr(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = ['close', 'high', 'low', 'stk_index_corr_zz500', 'adjfactor']
    normalize_size = 1210
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_high = data['high_preadj'].values[-362:]
        stk_low = data['low_preadj'].values[-362:]
        stk_close = data['close_preadj'].values[-362:]
        stk_index_corr_zz500 = data['stk_index_corr_zz500'].values[-362:]
        
        hh = ts_max(stk_high, 120)
        ll = ts_min(stk_low, 120)
        fac = 2 * stk_close / (hh + ll)
        facorg = rolling_norm(fac, 242)
        cr = section_rank_bk(stk_index_corr_zz500, pct=True) * 2 - 1
        fac = np.nansum(facorg * cr, axis=1)
        return fac[-1]
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

def get_norm(fa):
    fmax = np.nanmax(fa)
    fmin = np.nanmin(fa)
    divisor = fmax - fmin
    if divisor < 1e-8:
        divisior = np.nan
    return ((fa[-1] - fmin)/ divisor) * 2 - 1


class wyc_ts44_future(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close', 'volume']}
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[0,1]'
    handle_preadj = None 

    def calculate(self, df):
        volume = df['volume_cont_IC'][-1250:]
        close = df['close_cont_IC'][-1250:]
        temp1 = volume.copy(deep = True)
        con2 = close < close.shift(1)
        temp1[con2] = -1 * volume
        factor = bk.move_sum(temp1, 20, 10, axis = 0)[-1230:]
        factor = bk.move_mean(factor, 20, 10, axis = 0)[-1210:]
        factor = get_norm(factor)
        
        return factor

##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc11_future(FutureFactor):
    data_type = 'Future'
    days_past = 6
    data_dict = dict()
    instrument_type = 'recent'
    # data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low', 'open']}
    normalize_size = 1
    normalize_type = 'ts_rank'
#    num_range = '(-0.5,1]'
    
    def calculate(self, data):
        future_close = data['close_cont_IC'].values[-1314:]
        future_high = data['high_cont_IC'].values[-1314:]
        future_low = data['low_cont_IC'].values[-1314:]
        future_open = data['open_cont_IC'].values[-1314:]
        n = 20
        a = abs(future_high-ts_delay(future_close, 1))
        b = abs(future_low-ts_delay(future_close, 1))
        c = abs(future_high-ts_delay(future_low, 1))
        d = abs(ts_delay(future_close, 1)-ts_delay(future_open, 1))
        k = np.maximum(a, b)
        m = ts_max(future_high-future_low, n)
        r1 = a + 0.5 * b + 0.25 * d
        r2 = b + 0.5 * a + 0.25 * d
        r3 = c + 0.25 * d
        r4 = np.where((a>=b)&(a>=c), r1, r2)
        r = np.where((c>=a)&(c>=b), r3, r4)
        si = 50 * (ts_delta(future_close, 1) + ts_delay(future_close, 1) - ts_delay(future_open, 1)\
                   + 0.5*(future_close - future_open)) / r * k / m
        factor_mean = ts_mean(si, 90)
        factor_raw = ts_rank(factor_mean, 1200)
        return factor_raw[-1]

##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

class wsc4_spot(FutureFactor):

    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}    
    normalize_size = 1200
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    handle_preadj = None 
    
    def calculate(self, data):
        close = data['close_000905.SH'][-121:].values
        N = 20
        cmean = bk.move_mean(close, N, min_count=N//2, axis = 0)
        dpo = (close[11:] - cmean[:-11])[-90:]
        factor = abs(dpo - bk.move_median(dpo, 60, min_count=30, axis = 0))
        factor = np.nanmean(factor[-30:])
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:08:45 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd



class HmaxC_ind_nr_al_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 2
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','high', 'adjfactor','turnover_rate', 'amount']
    normalize_size = 242# normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        df_s = data['amount'].iloc[-60:].sum()
        
        turnover = (data['turnover_rate'].iloc[-60:].mean())
        temp1 = df_s.gt(df_s.quantile(0.80))
        temp4 = turnover.gt(turnover.quantile(0.80))
        bool_df = (temp1&temp4).values.astype(float)
        bool_df[bool_df==0] = np.nan
        hhigh = data['high_preadj'].iloc[-370:].values
        hclose = data['close_preadj'].iloc[-243:].values
        hmhm_r = -bk.move_max(hhigh, 120, min_count = 90, axis = 0)[-243:]/hclose
        hmhm_r = rolling_norm(hmhm_r, 242)[-1]
        factor = np.nanmean(hmhm_r*bool_df)
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:05:38 2021

@author: appadmin
"""


import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

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
##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd
import datetime
 
class wsc11_cfg_search_vr(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'adjfactor', 'stk_volatility']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        # mask
        volatility_mask = data['stk_volatility'][-15:]
        volatility_rank_mask = 2 * volatility_mask.rank(axis=1, pct=True).values - 1

        stk_close = data['close_preadj'][-50:].values
        stk_close_delta = stk_close[15:] - stk_close[:-15]
        factor_init = bk.move_max(stk_close_delta, 20, 10, axis = 0)

        factor_raw = np.nansum(factor_init[-15:] * volatility_rank_mask, axis=1)
        factor = np.nanmean(factor_raw)
     
        return factor
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_ts419_cs_cfg(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'high', 'low', 'volume', 'stk_index_corr_zz500', 'adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, df):
        close = df['close_preadj'][-40:]
        low = df['low_preadj'][-40:]
        high = df['high_preadj'][-40:]
        volume = df['volume_preadj'][-40:]
        
        cs = df['stk_index_corr_zz500'][-1:]
        
        factor = bk.move_sum(((close - low) - (high - close)) / (high - low) * volume, 10, 5, axis = 0)[-30:]
        finaldf = np.nanmean(factor, axis = 0)

        factor = finaldf * cs.values

        factor = np.nansum(factor, axis=1)
        return factor
##########
import numpy as np
from future_factor import FutureFactor


class wsc_search1_long(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 600
    normalize_type = 'rolling_norm'
#    num_range = '(-0.5,1]'
    
    def calculate(self, data):
        spot_close = data['close_000905.SH'].values[-45:]
        reg_x = np.arange(45) + 1.
        spot_close_centralized = spot_close - np.nanmean(spot_close)
        reg_x_centralized = reg_x - np.nanmean(reg_x)
        factor_raw = np.nansum(spot_close_centralized*reg_x_centralized) / np.nansum(reg_x_centralized**2)
        return factor_raw

##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc18_cfg_wr(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'open', 'high', 'low', 'weight', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '[-1,0.5)'
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-119:]
        stk_open = data['open_preadj'].values[-119:]
        stk_low = data['low_preadj'].values[-119:]
        stk_high = data['high_preadj'].values[-119:]
        stk_weight = data['weight'].values[-119:]
        weight_rank_mask = section_rank_np(stk_weight, pct=True) * 2 - 1
        n = 45
        a = abs(stk_high-ts_delay(stk_close, 1))
        b = abs(stk_low-ts_delay(stk_close, 1))
        c = abs(stk_high-ts_delay(stk_low, 1))
        d = abs(ts_delay(stk_close, 1)-ts_delay(stk_open, 1))
        k = np.maximum(a, b)
        m = ts_max(stk_high-stk_low, n)
        r1 = a + 0.5 * b + 0.25 * d
        r2 = b + 0.5 * a + 0.25 * d
        r3 = c + 0.25 * d
        r4 = np.where((a>=b)&(a>=c), r1, r2)
        r = np.where((c>=a)&(c>=b), r3, r4)
        si = 50 * (ts_delta(stk_close, 1) + ts_delay(stk_close, 1) - ts_delay(stk_open, 1) + 0.5*(stk_close - stk_open))\
            / replace_zero(r) * k / replace_zero(m)
        factor_raw = np.nansum(si * weight_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 70)
        return factor_mean[-1]

##########
import numpy as np
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


class wsc_fast14_spot(FutureFactor):

    data_type = 'Future' 
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'amount']}
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    
    def calculate(self, data):
        spot_close = data['close_000905.SH'].values[-20:]
        spot_high = data['high_000905.SH'].values[-20:]
        spot_low = data['low_000905.SH'].values[-20:]
        spot_amount = data['amount_000905.SH'].values[-20:]
        
        factor_raw = (2 * spot_close - spot_high - spot_low) / replace_zero(spot_high - spot_low) * spot_amount
        factor_mean = ts_mean(factor_raw, 20)
        return factor_mean[-1]
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc7_cfg_cr(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['stk_index_corr_zz500', 'close', 'high', 'low', 'adjfactor']
    normalize_size = 1800
    normalize_type = 'ts_rank'
#    num_range = '(-0.8,1]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-110:]
        stk_high = data['high_preadj'].values[-110:]
        stk_low = data['low_preadj'].values[-110:]
        stk_index_corr_zz500 = data['stk_index_corr_zz500'].values[-110:]
        stk_index_corr_rank_mask = section_rank_np(stk_index_corr_zz500, pct=True) * 2 - 1
        n = 20
        m = 60
        low_n = ts_min(stk_low, n)
        high_n = ts_max(stk_high, n)
        a = replace_zero(high_n - low_n)
        stochastics = (stk_close- low_n) / a
        stochastics_low = ts_min(stochastics, m)
        stochastics_high = ts_max(stochastics, m)
        c = replace_zero(stochastics_high - stochastics_low)
        stochastics_double = (stochastics - stochastics_low) / c
        factor_raw = np.nansum(stochastics_double * stk_index_corr_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 30)
        return factor_mean[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:01:19 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:09:30 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

    
class HLLSVol_CC(FutureFactor):

    data_type = 'Future'
    days_past = 2
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['high','low']} 
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '[0, 1]'
    instrument_type='recent'
    
    def calculate(self, data):
        hlow = (data['low_cont_IC'].values)[-250:]
        hhigh = (data['high_cont_IC'].values)[-250:]
        a = bk.move_std(hhigh/hlow, 240, min_count = 10)
        a[a<1e-10] = np.nan
        factor = bk.move_std(hhigh/hlow, 40, min_count = 10)/a
        return factor[-1]

##########
import bottleneck as bk
import numpy as np
from future_factor import FutureFactor

class ss1_cfg_zf(FutureFactor):
    '''
    成分股因子
    '''
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['close','high','amount','adjfactor']
    normalize_size = 242*5 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        close = data['close_preadj'].values[-242*6:]
        rtn = close[1:]/close[:-1]-1
        vol = bk.move_std(rtn, window = 60, min_count = 30, axis = 0)
        vol[vol < 1e-8] = 0
        high = data['high_preadj'].values[-242*6:]
        hh = bk.move_max(high[:-1],window = 60, min_count=30,axis=0)
        ret = close[1:]/hh-1
        facorg = ret/vol
        facorg = np.where((facorg == np.inf) | (facorg == -np.inf), np.nan, facorg)
        fac_max = bk.move_max(facorg, window = 242*5, min_count = 121*5, axis=0)
        fac_min = bk.move_min(facorg, window = 242*5, min_count = 121*5, axis=0)
        tmp = fac_max-fac_min
        tmp[np.abs(tmp)<1e-8]=np.nan
        facorg = (facorg-fac_min)/tmp*2-1

        amt_rank = (data['amount'].iloc[-5:].rank(axis=1,pct=True))*2-1
        ar = amt_rank.values
        fac = np.nansum(facorg[-5:]*ar,axis=1)
        return np.nanmean(fac)
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero


class wsc_ti9_cfg(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'open', 'low', 'weight', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-60:]
        stk_open = data['open_preadj'].values[-60:]
        stk_low = data['low_preadj'].values[-60:]
        stk_weight = data['weight'].values[-60:]
        x = stk_close - stk_open
        y = stk_open.copy()
        y = np.where(x<0, stk_close, y)
        z = replace_zero(y - stk_low)
        u = x / z
        factor_init = np.nansum(u * stk_weight, axis=1)
        factor_raw = ts_mean(factor_init, 60)
        return factor_raw[-1]


##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:31:01 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

### 先mask再rolling
class MALS_CC(FutureFactor):
    
    data_type = 'Future'
    instrument_type='recent'
    days_past = 12
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':[ 'close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    instrument_type='recent'
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
##########
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class stk2idx_amt_rank_a2p_zsj(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'close', 'adjfactor']
    normalize_size = 2400
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-50:]
        stk_close = data['close_preadj'].values[-50:]
        stk_amt_rank_short = bk.move_rank(stk_amount, 30, 27, axis=0)
        cut_line = np.nanmedian(stk_amount, axis=1, keepdims=True)
        active_raw = ma.array(stk_amt_rank_short, mask=(stk_amount<cut_line))
        inactive_raw = ma.array(stk_amt_rank_short, mask=(stk_amount>=cut_line))
        score = np.nanmean(active_raw, axis=1) - np.nanmean(inactive_raw, axis=1)
        factor_raw = -bk.move_mean(score, 20, 18)
        return factor_raw[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:01:01 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class L123_CFG2_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','amount','low', 'adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}
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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:58:05 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class HDLD_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'open', 'adjfactor', 'amount']
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
##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd
import datetime

def rolling_norm(sig, window=1200, method='max_min'):
    assert isinstance(sig, pd.Series) or isinstance(sig, pd.DataFrame) or isinstance(sig, np.ndarray), 'input must be a series, dataframe or ndarray'
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
            elif isinstance(sig, np.ndarray):
                sig_max = bk.move_max(sig, window=window, min_count=int(window / 2), axis=0)
                sig_min = bk.move_min(sig, window=window, min_count=int(window / 2), axis=0)
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
            elif isinstance(sig, np.ndarray):
                output = bk.move_rank(sig, window=d, min_count=int(d / 2), axis=0)
            return signal
        
class wyc_ts44_future_nr_as(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'adjfactor', 'volume', 'amount']
    normalize_size = 5 * 242 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, df):
        
        v = df['volume_preadj'][-1556:].values
        c = df['close_preadj'][-1556:].values
        
        factor = np.where(c[1:] < c[:-1], v[1:]*-1, v[1:])[-1555:]
        factor = bk.move_sum(factor, 20, 10, axis = 0)[-1535:]
        factor = bk.move_mean(factor, 20, 10, axis = 0)[-1515:]

        factor = rolling_norm(factor, 1210)[-305:]

        a = df['amount'][-305:].values
        factor = factor * a
        factor = np.nansum(factor, axis = 1)

        factor = bk.move_rank(factor, 300, 150, axis = 0)[-5:]
        factor = np.nanmean(factor)
      
        return factor
##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd
import scipy

class stk2indx_skew_zsj(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close','adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        ##### def data #####
        stk_close = data['close_preadj'][-26:]
        stk_ret = stk_close / stk_close.shift(1) - 1
        stk2indx_skew_raw = stk_ret.skew(axis=1).values
        ma = bk.move_mean(stk2indx_skew_raw,5,2,axis = 0)[-20:]
        factor = np.nanmean(ma)
        return factor
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd


class wyc_ts14_future(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 4
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close']} 
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 

    def calculate(self, df):
        close = df['close_cont_IC'][-806:]
        factor = np.where(close > close.shift(2), close.rolling(50, min_periods=25).std(), 0)[-756:]
        factor = bk.move_mean(factor, 30, 15, axis = 0)[-726:]
        factor = bk.move_rank(factor, 726, 363, axis = 0)[-1]
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:23:48 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

# 先mask后rolling
class CLP_CC(FutureFactor):

    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close','OpenInterest']}  
    normalize_size = 1200
    normalize_type = 'rolling_norm'
#    num_range = '[-0.3, 1]'
    instrument_type='recent'
    
    def calculate(self, data):
        
        hclose = (data['close_cont_IC'].values)[-30:]
        hclose = np.sign(hclose)
        position = (data['OpenInterest_cont_IC'].values)[-31:]

        temp3 = position[1:] - position[:-1]
        temp2 = np.abs(temp3*hclose)
        
        factor = np.nanmean(temp2)

        return factor
##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

def get_norm(fa):
    fmax = np.nanmax(fa)
    fmin = np.nanmin(fa)
    divisor = fmax - fmin
    if divisor < 1e-8:
        divisior = np.nan
    return ((fa[-1] - fmin)/ divisor) * 2 - 1

class wyc_ts25_future(FutureFactor):

    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close']}
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    handle_preadj = None 
    
    def calculate(self, df):
        c = df['close_cont_IC'][-1310:].values
        factor =  bk.move_mean(c, 20, min_count=10, axis = 0) / c
        factor = (bk.move_rank(factor[-1290:], 20, min_count=10, axis = 0) + 1)/2
        factor = bk.move_mean(factor[-1270:], 60, min_count=30, axis = 0)[-1210:]
        factor = get_norm(factor)
        return factor
##########
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_cc import *
from future_factor import FutureFactor


def r(data, x=np.nan):

    data[abs(data) < 1e-8] = x
    return data

    
class Short_BS10_CC(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['amount', 'buy_superorder_count', 'buy_bigorder_count', 'buy_midorder_count', 'buy_smallorder_count']
    normalize_size = 1200 
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False

    def calculate(self, data):
        stk_amount = data['amount'].values[-93:]
        stk_buy_superorder_count = data['buy_superorder_count'].fillna(0).values[-93:]
        stk_buy_bigorder_count = data['buy_bigorder_count'].fillna(0).values[-93:]
        stk_buy_midorder_count = data['buy_midorder_count'].fillna(0).values[-93:]
        stk_buy_smallorder_count = data['buy_smallorder_count'].fillna(0).values[-93:]

        amount_sum = bk.move_sum(stk_amount, window=90, min_count=15, axis=0)
        amount_mask = np.nanquantile(amount_sum, 0.9, axis=1)
        amount_mask = np.expand_dims(amount_mask, axis=-1)
        alll = r(stk_buy_superorder_count + stk_buy_bigorder_count + stk_buy_midorder_count + stk_buy_smallorder_count)
        temp2 = stk_buy_smallorder_count / alll
        temp2_after_mask = ma.array(temp2, mask=(amount_sum<=amount_mask))
        factor_raw = np.nanmean(temp2_after_mask, axis=1)
        factor_mean = -bk.move_mean(factor_raw, window=3, min_count=1, axis=0)
        return factor_mean[-1]
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_hf3(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['Ask1AmtMean']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        stk_Ask1AmtMean = data['Ask1AmtMean'].values[-75:]
        a = np.nansum(stk_Ask1AmtMean, axis=1)
        factor_init = ts_rank(a, 30)
        factor_raw = -ts_mean(factor_init, 45)
        return factor_raw[-1]
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:25:42 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class LSC_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 5
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['high','close', 'low']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '[0, 1]'
    instrument_type='recent'
    
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
    
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc19_cfg_as(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'amount', 'adjfactor']
    normalize_size = 1000
    normalize_type = 'ts_rank'
#    num_range = '(-0.64,1]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-48:]
        stk_amount = data['amount'].values[-48:]
        n = 30
        arron_up = ts_argmax(stk_close, n) / n * 100  # 过去n分钟最高价出现时间与当前时间的距离占时间段长度的比例
        arron_down = ts_argmin(stk_close, n) / n * 100  # 过去n分钟最低价出现时间与当前时间的距离占时间段长度的比例
        arron_os = arron_up - arron_down
        factor_raw = np.nansum(arron_os * stk_amount, axis=1)
        factor_mean = ts_mean(factor_raw, 18)
        return factor_mean[-1]
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:58:53 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class HL123_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['high', 'low','adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.5, 1]'# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
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

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:08:30 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd



class CFG16_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','low', 'adjfactor']
    normalize_size = 1200# normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.5, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        hlow = data['low_preadj'].iloc[-1320:].values
        hclose = data['close_preadj'].iloc[-1321:].values
        hret = hclose[1:]/hclose[:-1]-1
        i1 = -bk.move_min(hlow, 60, min_count = 15, axis = 0)/bk.move_mean(hlow, 30, min_count = 10, axis = 0)
        i1 = pd.DataFrame(i1, index =  data['low_preadj'].iloc[-1320:].index, columns = data['low_preadj'].columns)
        #hret = pd.DataFrame(hret, index =  data['low_preadj'].iloc[-1320:].index, columns = data['low_preadj'].columns)
        i2 = to_ts(i1, hret)
        i2 = rolling_norm(bk.move_mean(i2, 30, min_count = 15, axis = 0), method = 'ts_rank')

        factor = np.nanmean(i2[-5:])
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:48:00 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:53:36 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd



class CFG8_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 10
    data_dict = dict()
    data_dict['Stock'] = ['float_shares', 'volume', 'close', 'adjfactor']
    #data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.5, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
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
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk

def get_norm(fa):
    fmax = np.nanmax(fa)
    fmin = np.nanmin(fa)
    divisor = fmax - fmin
    if divisor < 1e-8:
        divisior = np.nan
    return ((fa[-1] - fmin)/ divisor) * 2 - 1

class wyc_icc_ifv_corr(FutureFactor):
    
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close'],'IF':['volume']} 
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 

    def calculate(self, df):
        volume = df['volume_cont_IF'][-5*242 - 70:]
        close = df['close_cont_IC'][-5*242 - 70:]
        s = volume.rolling(60, min_periods=30).std()
        f = close.rolling(60, min_periods=30).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        factor = volume.rolling(60, min_periods=30).cov(close) / (s * f)
        factor = -1 * factor
        factor = get_norm(factor.values[-5*242:])
        
        return factor


##########
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_cc import *
from operators_wsc_1_0 import ts_pct_change
from future_factor import FutureFactor

def r(data, x=np.nan):

    data[abs(data) < 1e-8] = x
    return data

    
class Short_CFG7_CC(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['turnover_rate', 'close', 'open', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        stk_close = data['close_preadj'].values[-82:]
        stk_open = data['open_preadj'].values[-82:]
        stk_turnover = data['turnover_rate'].values[-82:]
        
        ret = stk_close / stk_open - 1
        hret = ts_pct_change(stk_close, 1)
        stk_turnover[stk_close >= stk_open] = np.nan
        ret[stk_close >= stk_open] = np.nan
        cc1 = stk_turnover / r(abs(ret))
        ccc1 = bk.move_mean(cc1, 60, 7, axis=0)
        ccc1_mask = np.expand_dims(np.nanmedian(ccc1, axis=1), axis=-1)
        hret1 = ma.array(hret, mask=(ccc1<=ccc1_mask))
        hret2 = ma.array(hret, mask=(ccc1>=ccc1_mask))
        cc2 = np.nanmean(hret1, axis=1) - np.nanmean(hret2, axis=1)
        ccc2 = bk.move_mean(cc2, 20, 10)
        return ccc2[-1]
##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

class stk2idx_ret_jump_a2p_chg_zsj(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close','adjfactor','amount']
    normalize_size = 2400
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        stk_close = data['close_preadj'][-120:]
        stk_amt = data['amount'][-120:]

        cut_line = stk_amt.median(axis=1)
        active_mask = stk_amt.subtract(cut_line, axis=0) >= 0
        inactive_mask = stk_amt.subtract(cut_line, axis=0) < 0

        stk_ret_short = stk_close/stk_close.shift(5) - 1
        stk_ret_long = stk_close/stk_close.shift(30) - 1
        stk_ret_jump = stk_ret_short - stk_ret_long

        score_raw = stk_ret_jump
        mask1 = active_mask
        mask2 = inactive_mask
        active_raw = score_raw[mask1].mean(axis=1)
        inactive_raw = score_raw[mask2].mean(axis=1)
        stk2idx_ret_jump_a2p_raw = (inactive_raw - active_raw)[-90:]
        factor = np.nanmean(stk2idx_ret_jump_a2p_raw[-10:]) - np.nanmean(stk2idx_ret_jump_a2p_raw)

        return factor
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc12_cfg_vr(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['stk_volatility', 'close', 'high', 'low', 'open', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-45:]
        stk_high = data['high_preadj'].values[-45:]
        stk_low = data['low_preadj'].values[-45:]
        stk_open = data['open_preadj'].values[-45:]
        stk_volatility = data['stk_volatility'].values[-45:]
        stk_volatility_rank_mask = section_rank_np(stk_volatility, pct=True) * 2 - 1
        stk_price = (stk_high + stk_low + stk_open + stk_close) / 4
        n = 30
        rpp = ts_sum(stk_price, n)
        high_n = ts_max(stk_high, n)
        low_n = ts_min(stk_low, n)
        temp = replace_zero(high_n - low_n)
        arpp = (rpp - low_n) / temp
        factor_raw = np.nansum(arpp * stk_volatility_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        return factor_mean[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:05:48 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd
  

class CloseVoltoMean_IFIC_CC(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']} 
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    instrument_type='recent'
    #num_range = [-0.2, 1]
    
    def calculate(self, data):
        
        hclose = (data['close_000300.SH'].values)[-41:]
        return np.nanmean((bk.move_std(hclose, 30, min_count = 10, axis = 0)/bk.move_mean(hclose, 30, min_count = 15, axis = 0))[-10:])


##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:07:33 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd



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
##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd
import datetime

def rolling_norm(sig, window=1200, method='max_min'):
    assert isinstance(sig, pd.Series) or isinstance(sig, pd.DataFrame) or isinstance(sig, np.ndarray), 'input must be a series, dataframe or ndarray'
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
            elif isinstance(sig, np.ndarray):
                sig_max = bk.move_max(sig, window=window, min_count=int(window / 2), axis=0)
                sig_min = bk.move_min(sig, window=window, min_count=int(window / 2), axis=0)
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
            elif isinstance(sig, np.ndarray):
                output = bk.move_rank(sig, window=d, min_count=int(d / 2), axis=0)
            return signal
        
class wyc_ts14_future_nr_cr(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 6
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'adjfactor', 'stk_index_corr_zz500']
    normalize_size = 5 * 242 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, df):

        c = df['close_preadj'][-1270:].values
        s = bk.move_std(c, 50, 25, axis = 0)[2:]
        factor = np.where(c[2:] > c[:-2], s, 0)
        factor = bk.move_mean(factor, 30, 15, axis = 0)[-1211:]

        factor = rolling_norm(factor, 1210)[-1:]

        cr = (2 * df['stk_index_corr_zz500'][-1:].rank(axis=1, pct=True) - 1)
        factor = factor * cr
        factor = np.nansum(factor, axis = 1)
        return factor
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *


class wsc1_cfg_wr(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'weight', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-90:]
        stk_weight = data['weight'].values[-90:]
        weight_rank_mask = 2 * section_rank_np(stk_weight, pct=True) - 1
        close_ma_long = ts_mean(stk_close, 90)
        close_ma_short = ts_mean(stk_close, 15)
        close_ma_diff = close_ma_short - close_ma_long
        factor_raw = np.nansum(close_ma_diff[-1] * weight_rank_mask[-1])
        return factor_raw

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 18:15:27 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class HcorrC_IFIC_CC(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['close', 'high']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    instrument_type='recent'
    
    def calculate(self, data):
        hclose = (data['close_cont_IF']).iloc[-60:]
        hhigh = (data['high_cont_IF']).iloc[-60:]
        factor = hclose.corr(hhigh)
        return factor
##########
import numpy as np
import bottleneck as bk
from operators_wsc_1_0 import *
from future_factor import FutureFactor


def section_rank_bk(data, pct=False):
    # numpy的argsort函数在值相同的情况下会出现排序不稳定的情况，所以用bk.rankdata代替，对应df.rank(method='first')
    if not isinstance(data, np.ndarray):
        raise TypeError('Only supports the following type: np.ndarray')
    data_argsort = bk.rankdata(data, axis=1)  # +1是因为numpy从0计数，pandas从1计数
    data_argsort[np.isnan(data)] = np.nan  # numpy argsort会让nan也参与排序，但是pandas不会，所以把这些值重新置为nan
    if pct == True:
        data_argsort = data_argsort / (~np.isnan(data)).sum(axis=1, keepdims=True)
    return data_argsort


class Short_ss1_cfg_zf(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 6
    data_dict = dict()
    data_dict['Stock'] = ['close', 'high', 'amount', 'adjfactor']
    normalize_size = 1210
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-1272:]
        stk_close = data['close_preadj'].values[-1272:]
        stk_high = data['high_preadj'].values[-1272:]
        
        rtn = ts_pct_change(stk_close, 1)
        vol = ts_std(rtn, 60)
        ret = stk_close / ts_max(ts_delay(stk_high, 1), 60) - 1
        factorg = rolling_norm(ret / vol, 1210)
        ar = section_rank_bk(stk_amount, pct=True) * 2 - 1
        fac = np.nansum(factorg * ar, axis=1)
        return fac[-1]
##########
import numpy as np
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor



class wyc_bigon_cfghf_fast(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeNum', 'BuyUniqueOrderNum']
    normalize_size = 237 * 3
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        stk_BuyTradeNum = data['BuyTradeNum'].values[-1]
        stk_BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-1]
        
        btn = replace_zero(stk_BuyTradeNum)
        factor_raw = 1 - stk_BuyUniqueOrderNum / btn
        factor_raw = np.nansum(factor_raw)
        return factor_raw
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class amihund_measure_zsj(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close','amount']}
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 

    def calculate(self, data):
        close = data['close_cont_IC'][-1290:]
        amount = data['amount_cont_IC'][-1290:]
        minute_ret = close / close.shift(1) - 1

        ret_pos = minute_ret > 0
        amount = amount.replace({0: np.nan})
        amihund_measure_raw = minute_ret / amount

        amihund_measure_raw_ma = bk.move_mean(amihund_measure_raw, 90, 81, axis = 0)
        factor = bk.move_rank(amihund_measure_raw_ma, 1200, 1080, axis = 0)[-1]
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:55:10 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd



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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:35:19 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class td_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Index_Id'] = {'000300.SH':['close']}
    data_dict['Continuous_Data'] = {'IC':['low', 'high']}
    normalize_size = 1200
    normalize_type = 'rolling_norm'
#    num_range = '[-0.5, 1]'
    instrument_type='recent'
    
    def calculate(self, data):
        hlow = (data['low_cont_IC'].values)[-60:]
        hhigh = (data['high_cont_IC'].values)[-60:]
        templ = np.nanmin(hlow[-10:]) - np.nanmin(hlow)
        temph = np.nanmax(hhigh[-10:]) - np.nanmax(hhigh)
        factor = templ+temph
        return factor
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc16_cfg_search_vr(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'stk_volatility', 'adjfactor']
    normalize_size = 1800
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-35:]
        stk_volatility = data['stk_volatility'].values[-35:]
        stk_volatility_rank_mask = section_rank_np(stk_volatility, pct=True) * 2 - 1 
        factor_init = ts_reg_beta(stk_close, 15)
        factor_raw = np.nansum(factor_init * stk_volatility_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 20)
        return factor_mean[-1]

##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc1_cfg_vr(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'stk_volatility', 'adjfactor']
    normalize_size = 900
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-80:]
        volatility_mask = data['stk_volatility'].values[-80:]
        volatility_rank_mask = 2 * section_rank_np(volatility_mask, pct=True) - 1
        close_ma_long = ts_mean(stk_close, 75)
        close_ma_short = ts_mean(stk_close, 10)
        close_ma_diff = close_ma_short - close_ma_long
        factor_init = np.nansum(close_ma_diff * volatility_rank_mask, axis=1)
        factor_raw = ts_mean(factor_init, 5)
        return factor_raw[-1]


##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:50:01 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


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


##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:02:30 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class CDO_CC(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['close', 'open']} 
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
#    num_range = '(-0.5, 1]'
    instrument_type='recent'
                   
    def calculate(self, data):
        
        hclose = data['close_cont_IC'].values[-120:]
        hopen = data['open_cont_IC'].values[-120:]
        factor = np.nanmean(hclose)/np.nanmean(hopen)

        return factor
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd
from joblib import Parallel, delayed

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
    assert isinstance(df, pd.DataFrame), 'the data structure of input is illegal, must be dataframe'
    results = Parallel(n_jobs=n_jobs)(delayed(func)(df[i], **kwargs) for i in df.columns)
    results_df = pd.DataFrame(results, index=df.columns, columns=df.index)
    return results_df.T

class wyc_ts6_future_ts(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['close', 'turnover_rate', 'high', 'low', 'volume', 'adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True 

    def calculate(self, df):
        a = df['high_preadj'][-1625:] - df['low_preadj'][-1625:]
        a[abs(a) < 1e-8] = np.nan
        factor = df['volume_preadj'][-1625:] * ((df['close_preadj'][-1625:] - df['low_preadj'][-1625:]) - (df['high_preadj'][-1625:] - df['close_preadj'][-1625:])) / a
        factor = multi_processing_joblib(df=factor, func=ts_truncated_ema, n_jobs=-1, d=200, alpha= 1/45).values[-1425:]
        factor = bk.move_rank(factor, 1200, 600, axis = 0)[-225:]
        factor = bk.move_mean(factor, 15, 7, axis = 0)[-210:]

        t = df['turnover_rate'].values[-210:]
        factor = factor * t
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 200, 100, axis = 0)[-10:]
        factor = np.nanmean(factor)

        return factor
##########
import numpy as np
from future_factor import FutureFactor

    
class wsc7_spot(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['amount']}
    normalize_size = 1150
    normalize_type = 'ts_rank'
#    num_range = '(-0.5,1]'
    
    def calculate(self, data):
        spot_amount = data['amount_000905.SH'].values[-20:]
        return np.nanmax(spot_amount)

##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd
import scipy


class Short_GA_CFG_2_CC(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Stock'] = ['close','adjfactor','open','high','low']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 240
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        index_close = data['close_000905.SH'][-1203:]
        stk_close = data['close_preadj'][-1203:]
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.iloc[-1200:].corrwith(index_ret.iloc[-1200:,0])
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        bool_df = stk_index_corr[stk_index_corr>stk_index_corr.quantile(0.95)]
        bool_stk_list = bool_df.index.to_list()
        
        high = data['high_preadj'][-31:]
        close = data['close_preadj'][-31:]
        opendf = data['open_preadj'][-31:]
        low = data['low_preadj'][-31:]
        a = high.rolling(30, min_periods = 15).max()-opendf.shift(30)
        b = close - low.rolling(30, min_periods = 15).min()
        c = (high.rolling(30, min_periods = 15).max()-low.rolling(30, min_periods = 15).min())*2
        vwtc_r = (a[-1:]+b[-1:])/c[-1:]
        vwtc_r = vwtc_r.replace([-np.inf, np.inf], np.nan)
        factor = np.nanmean(vwtc_r[bool_stk_list].values)
        return factor
##########
import numpy as np
import numpy.ma as ma
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_cfg5(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'weight', 'amount', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-23:]
        stk_amount = data['amount'].values[-23:]
        stk_weight = data['weight'].values[-23:]
        stk_ret = ts_pct_change(stk_close, 3)
        stk_ret_mask = np.nanquantile(stk_ret, 0.9, axis=1)
        stk_ret_mask = np.expand_dims(stk_ret_mask, axis=-1)
        amount_after_mask = ma.array(stk_amount, mask=(stk_ret<=stk_ret_mask))
        factor_raw = np.nansum(amount_after_mask * stk_weight, axis=1)
        factor_raw = ts_mean(factor_raw, 20)
        return factor_raw[-1]

##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd
import datetime
 
class wsc2_cfg_vr(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'adjfactor', 'stk_volatility']
    normalize_size = 1800 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        # mask
        volatility_mask = data['stk_volatility'][-16:]
        volatility_rank_mask = 2 * volatility_mask.rank(axis=1, pct=True).values - 1
            
        # as follows
        a = data['close_preadj'][-50:].values
        a = a[3:] / a[:-3] - 1
        b = bk.move_mean(a, 30, 15, axis = 0)
        c = bk.move_std(a, 30, 15, axis = 0)
        factor_init = 4 * b + c
        factor_raw = np.nansum(factor_init[-16:] * volatility_rank_mask[-16:], axis=1)
        factor = np.nanmean(factor_raw)
     
        return factor
##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

def get_norm(fa):
    fmax = np.nanmax(fa)
    fmin = np.nanmin(fa)
    divisor = fmax - fmin
    if divisor < 1e-8:
        divisior = np.nan
    return ((fa[-1] - fmin)/ divisor) * 2 - 1

class wsc_tsmax_amount(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['amount']}
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    handle_preadj = None 
    
    def calculate(self, df):
        factor = df['amount_cont_IC'][-165:].values
        factor = bk.move_max(factor, 45, min_count=22, axis = 0)[-120:]
        factor = get_norm(factor)
        return factor
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero


class wsc18_cfg_as(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'open', 'high', 'low', 'amount', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '(-0.7,1]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-69:]
        stk_open = data['open_preadj'].values[-69:]
        stk_low = data['low_preadj'].values[-69:]
        stk_high = data['high_preadj'].values[-69:]
        stk_amount = data['amount'].values[-69:]
        n = 20
        a = abs(stk_high-ts_delay(stk_close, 1))
        b = abs(stk_low-ts_delay(stk_close, 1))
        c = abs(stk_high-ts_delay(stk_low, 1))
        d = abs(ts_delay(stk_close, 1)-ts_delay(stk_open, 1))
        k = np.maximum(a, b)
        m = ts_max(stk_high-stk_low, n)
        r1 = a + 0.5 * b + 0.25 * d
        r2 = b + 0.5 * a + 0.25 * d
        r3 = c + 0.25 * d
        r4 = np.where((a>=b)&(a>=c), r1, r2)
        r = np.where((c>=a)&(c>=b), r3, r4)
        si = 50 * (ts_delta(stk_close, 1) + ts_delay(stk_close, 1) - ts_delay(stk_open, 1) + 0.5*(stk_close - stk_open))\
            / replace_zero(r) * k / replace_zero(m)
        factor_raw = np.nansum(si * stk_amount, axis=1)
        factor_mean = ts_mean(factor_raw, 45)
        return factor_mean[-1]
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class high_low_diff_stk2idx_zsj(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 11
    data_dict = dict()
    data_dict['Stock'] = ['close', 'open', 'high', 'low', 'amount', 'adjfactor'] 
    normalize_size = 800
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        stk_close = data['close_preadj'][-2460:]
        stk_high = data['high_preadj'][-2460:]
        stk_low = data['low_preadj'][-2460:]
        stk_open = data['open_preadj'][-2460:]
        stk_amt = data['amount'][-2460:]

        high_open_diff = stk_high - stk_open
        open_low_diff = stk_open - stk_low
        high_low_diff_stk = bk.move_sum(high_open_diff, 30, 15, axis = 0) - bk.move_sum(open_low_diff, 30, 15, axis = 0)
        high_low_diff_stk2idx_raw = np.nanmean(high_low_diff_stk, axis=1)[-2430:]
        
        mma = bk.move_mean(high_low_diff_stk2idx_raw, 30, 27, axis = 0)[-2400:]
        factor = bk.move_rank(mma, 2400, 2160, axis=0)[-1]

        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:48:36 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class CFG18_CC(FutureFactor):
    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['high','close','weight','adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.5, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
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
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk

def get_norm(fa):
    fmax = np.nanmax(fa)
    fmin = np.nanmin(fa)
    divisor = fmax - fmin
    if divisor < 1e-8:
        divisior = np.nan
    return ((fa[-1] - fmin)/ divisor) * 2 - 1

class wyc_ihcv_corr(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 4
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IH':['close','volume']} 
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[-0.5,1]'
    handle_preadj = None 

    def calculate(self, df):
        volume = df['volume_cont_IH'][-3*242 - 60:]
        close = df['close_cont_IH'][-3*242 - 60:]
        s = volume.rolling(30, min_periods=15).std()
        f = close.rolling(30, min_periods=15).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        factor = volume.rolling(30, min_periods=15).cov(close) / (s * f)
        factor = -1 * bk.move_mean(factor.values, 10, 5, axis = 0)
        factor = get_norm(factor[-3*242:])
        return factor
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc18_cfg_ar(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'open', 'high', 'low', 'amount', 'adjfactor']
    normalize_size = 650
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-99:]
        stk_open = data['open_preadj'].values[-99:]
        stk_low = data['low_preadj'].values[-99:]
        stk_high = data['high_preadj'].values[-99:]
        stk_amount = data['amount'].values[-99:]
        amount_rank_mask = section_rank_np(stk_amount, pct=True) * 2 - 1
        n = 45
        a = abs(stk_high-ts_delay(stk_close, 1))
        b = abs(stk_low-ts_delay(stk_close, 1))
        c = abs(stk_high-ts_delay(stk_low, 1))
        d = abs(ts_delay(stk_close, 1)-ts_delay(stk_open, 1))
        k = np.maximum(a, b)
        m = ts_max(stk_high-stk_low, n)
        r1 = a + 0.5 * b + 0.25 * d
        r2 = b + 0.5 * a + 0.25 * d
        r3 = c + 0.25 * d
        r4 = np.where((a>=b)&(a>=c), r1, r2)
        r = np.where((c>=a)&(c>=b), r3, r4)
        si = 50 * (ts_delta(stk_close, 1) + ts_delay(stk_close, 1) - ts_delay(stk_open, 1) + 0.5*(stk_close - stk_open))\
            / replace_zero(r) * k / replace_zero(m)
        factor_raw = np.nansum(si * amount_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 50)
        return factor_mean[-1]

##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_ts419_ar_cfg(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'high', 'low', 'volume', 'amount', 'adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[-0.5,1]'
    handle_preadj = True

    def calculate(self, df):
        close = df['close_preadj'][-60:]
        low = df['low_preadj'][-60:]
        high = df['high_preadj'][-60:]
        volume = df['volume_preadj'][-60:]
        
        amount = df['amount'][-20:]
        
        factor = bk.move_sum(((close - low) - (high - close)) / (high - low) * volume, 10, 5, axis = 0)[-50:]
        finaldf = bk.move_mean(factor, 30, 15, axis = 0)[-20:]

        factor = finaldf * (2 * amount.rank(axis=1, pct=True).values - 1)

        factor = np.nansum(factor, axis=1)
        factor = np.nanmean(factor)

        return factor
##########
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_cc import *
from operators_wsc_1_0 import ts_pct_change
from future_factor import FutureFactor


class Short_cmh_ae_CFG_CC(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 6
    data_dict = dict()
    data_dict['Stock'] = ['amount', 'turnover_rate', 'close', 'high', 'adjfactor']
    normalize_size = 242
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        stk_close = data['close_preadj'].values[-1382:]
        stk_high = data['high_preadj'].values[-1382:]
        stk_amount = data['amount'].values[-1382:]
        stk_turnover = data['turnover_rate'].values[-1382:]
        
        df_s = bk.move_sum(stk_amount, 120, 15, axis=0)
        temp1 = np.nanquantile(df_s, 0.8, axis=1)
        temp1 = np.expand_dims(temp1, axis=-1)
        ret_30 = ts_pct_change(stk_turnover, 30)
        temp5 = np.nanquantile(ret_30, 0.8, axis=1)
        temp5 = np.expand_dims(temp5, axis=-1)
        vwtc_r = stk_high - bk.move_mean(stk_close, 180, 30, axis=0)
        vwtc_r_min = bk.move_min(vwtc_r, 1200, 600, axis=0)
        vwtc_r_max = bk.move_max(vwtc_r, 1200, 600, axis=0)
        vwtc_r = (vwtc_r - vwtc_r_min) / (vwtc_r_max - vwtc_r_min)
        factor = ma.array(vwtc_r, mask=(df_s<=temp1)|(ret_30<=temp5))
        factor = np.nanmean(factor, axis=1)
        factor = bk.move_mean(factor, 2, 1)
        return factor[-1]
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd
    
class wyc_ts44_future_s(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'volume', 'adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[0,1]'
    handle_preadj = True

    def calculate(self, df):
        volume = df['volume_preadj'][-40:]
        close = df['close_preadj'][-40:]
        temp1 = volume.copy(deep = True)
        con2 = close < close.shift(1)
        temp1[con2] = -1 * volume
        
        factor = bk.move_sum(temp1, 20, 10, axis = 0)[-20:]
        factor = np.nanmean(factor, axis = 0)

        factor = np.nansum(factor)

        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:32:29 2021

@author: appadmin
"""


import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class Rev_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 11
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':[ 'close']}
    normalize_size = 2420
    normalize_type = 'rolling_norm'
#    num_range = '[-0.5, 1]'
    instrument_type='recent'
    
    def calculate(self, data):
        hclose = data['close_cont_IC'].iloc[-190:]
        ret = (hclose/hclose.shift(180)-1).values
        #print(shift(hclose, 180))
        factor = bk.move_mean(ret, 3, min_count = 2)
        #print(factor[-1])
        return factor[-1]
    
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:07:48 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:00:07 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


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
##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd
 
class wyc_if_2hour_return_as_150_20_cfg(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = ['close','amount','adjfactor']
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, df):
        cif = df['close_preadj'].values
        cif[abs(cif) < 1e-8] = np.nan
        ifreturn = cif[1:] / cif[:-1] - 1
        factor = bk.move_mean(ifreturn, 200, min_count=100, axis = 0)

        a = df['amount'].values
        factor = factor * a[1:]
        factor = np.nansum(factor,axis = 1)

        factor = bk.move_rank(factor[-170:], 150, 25, axis = 0)
        factor = np.nanmean(factor[-20:])

        return factor
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

def rolling_norm(sig, window=1200, method='max_min'):
    assert isinstance(sig, pd.Series) or isinstance(sig, pd.DataFrame) or isinstance(sig, np.ndarray), 'input must be a series, dataframe or ndarray'
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
            elif isinstance(sig, np.ndarray):
                sig_max = bk.move_max(sig, window=window, min_count=int(window / 2), axis=0)
                sig_min = bk.move_min(sig, window=window, min_count=int(window / 2), axis=0)
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
            elif isinstance(sig, np.ndarray):
                output = bk.move_rank(sig, window=d, min_count=int(d / 2), axis=0)
            return signal
        
        
class xdy_ts13_future_nr_as_300_10(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 11
    data_dict = dict()
    data_dict['Stock'] = ['high','amount','adjfactor']
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, df):
        high = df['high_preadj'][-2401:].values
        factor = bk.move_max(high, 121, 60, axis = 0)[-2280:]
        factor = rolling_norm(factor, 3*242)[-1554:]
        factor = factor[15:] - factor[:-15]
        factor = bk.move_max(factor, 19, 9, axis = 0)[-1520:]
        
        factor = rolling_norm(factor, 5 * 242)[-310:]

        a = df['amount'][-310:].values
        factor = factor * a
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 300, 150, axis = 0)[-10:]
        factor = np.nanmean(factor)
        
        return factor
    
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero, replace_inf




class wsc_hf11(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'SellTradeMoney']
    normalize_size = 900
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        stk_close = replace_zero(data['close'].values[-37:])
        stk_SellTradeMoney = data['SellTradeMoney'].iloc[-37:].fillna(0).values  # fillna是因为之前研究用的数据是这么处理的
        stk_ret = replace_inf(ts_pct_change(stk_close, 1))
        # x = (stk_SellTradeMoney.rank(axis=1, pct=True) * 2 - 1).values
        x = section_rank_np(stk_SellTradeMoney, pct=True) * 2 - 1
        factor_init = np.nansum(x*stk_ret, axis=1)
        factor_raw = ts_mean(factor_init, 36)
        return factor_raw[-1]
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:03:03 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class RolTrendLS_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 10
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'low', 'high','open', 'amount', 'adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}
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
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc20_cfg_vs(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Stock'] = ['close', 'stk_volatility', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '[-1,0]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-60:]
        spot_close = data['close_000905.SH'].values[-60:]
        stk_volatility = data['stk_volatility'].values[-60:]
        stk_ret = ts_pct_change(stk_close, 45)
        spot_ret = ts_pct_change(spot_close, 45)
        excess_ret = stk_ret - spot_ret
        stk_volatility[np.isnan(excess_ret)] = np.nan
        stk_volatility[excess_ret >= 0] = 0
        factor_raw = np.nansum(stk_volatility, axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        return factor_mean[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 17:55:23 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

    
class CLSH_CC(FutureFactor):

    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close', 'share']}
    normalize_size = 242*3
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        hclose = data['close_cont_IC'].iloc[-1001:].values
        temp1 = (np.where(np.diff(hclose)>0, 1, np.where(np.diff(hclose)<0, -1, 0)))
        
        hshare = data['share_cont_IC'].iloc[-1000:].values

        temp2 = np.abs(hshare * temp1)
        hdl_ind_r = bk.move_mean(temp2, 30, min_count = 15, axis = 0)

        factor = rolling_norm(hdl_ind_r, 242*4)
        factor = np.nanmean(factor[-5:])
        return factor
##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

class wsc_return_comparison(FutureFactor):

    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close'],'000300.SH':['close']}    
    normalize_size = 1200
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    handle_preadj = None 
    
    def calculate(self, data):
        a = data['close_000905.SH'][-193:].values
        b = data['close_000300.SH'][-193:].values
        a = a[3:] / a[:-3] - 1
        b = b[3:] / b[:-3] - 1
        c = a - b
        c[c > 0] = 1
        c[c <= 0] = 0
        temp = bk.move_sum(c, 180, min_count=90, axis = 0)
        temp[abs(temp)<1e-8] = np.nan
        factor = bk.move_sum(c, 30, min_count=15, axis = 0) / temp
        factor = np.nanmean(factor[-10:])
        return factor
##########
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_cc import *
from operators_wsc_1_0 import ts_pct_change
from future_factor import FutureFactor


class Short_CFG16_CC(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 6
    data_dict = dict()
    data_dict['Stock'] = ['close', 'low', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-1296:]
        stk_low = data['low_preadj'].values[-1296:]
        
        hret = ts_pct_change(stk_close, 1)
        i1 = -bk.move_min(stk_low, 90, 15, axis=0) / bk.move_mean(stk_low, 60, 10, axis=0)
        i1_mask = np.nanmedian(i1, axis=1)
        i1_mask = np.expand_dims(i1_mask, axis=-1)
        hret_up_after_mask = ma.array(hret, mask=(i1<=i1_mask))
        hret_down_after_mask = ma.array(hret, mask=(i1>=i1_mask))
        i2 = np.nanmean(hret_up_after_mask, axis=1) - np.nanmean(hret_down_after_mask, axis=1)
        i2 = bk.move_rank(i2, 1200, 600)
        i2 = bk.move_mean(i2, 6, 2)
        return i2[-1]
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk

def get_norm(fa):
    fmax = np.nanmax(fa)
    fmin = np.nanmin(fa)
    divisor = fmax - fmin
    if divisor < 1e-8:
        divisior = np.nan
    return ((fa[-1] - fmin)/ divisor) * 2 - 1

class wyc_ifcv_corr2(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 4
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['close','volume']} 
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[-0.5,1]'
    handle_preadj = None 

    def calculate(self, df):
        volume = df['volume_cont_IF'][-3*242 - 60:]
        close = df['close_cont_IF'][-3*242 - 60:]
        s = volume.rolling(30, min_periods=15).std()
        f = close.rolling(30, min_periods=15).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        factor = volume.rolling(30, min_periods=15).cov(close) / (s * f)
        factor = -1 * bk.move_mean(factor.values, 10, 5, axis = 0)
        factor = get_norm(factor[-3*242:])
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:35:38 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class vc_ind_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['volume', 'close']}
    #data_dict['Continuous_Data'] = {'IC':['low', 'high']}
    normalize_size = 1200
    normalize_type = 'rolling_norm'
#    num_range = '[-1, 1]'
    
    def calculate(self, data):
        hvolume = (data['volume_000905.SH'].values)[-20:]
        hclose = (data['close_000905.SH'].values)[-20:]
        factor = bk.move_mean((hvolume-shift(hvolume, 1)), 15, min_count = 7)*(hclose - shift(hclose, 15))
        return -factor[-1]
    

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:31:47 2021

@author: appadmin
"""


import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:54:31 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class CrossingTurns_CFG_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 10
    data_dict = dict()
    data_dict['Stock'] = [ 'amount', 'close', 'open', 'high', 'low','adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.5, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
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
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc_hf2(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['BuyTradeNum', 'weight', 'BuyUniqueOrderNum']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        stk_BuyTradeNum = data['BuyTradeNum'].values[-25:]
        stk_BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-25:]
        stk_weight = data['weight'].values[-25:]
        buow = replace_zero(np.nansum(stk_BuyUniqueOrderNum*stk_weight, axis=1))
        factor_init = np.nansum(stk_BuyTradeNum * stk_weight, axis=1) / buow
        factor_raw = ts_mean(factor_init, 25)
        return factor_raw[-1]
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *


class wsc5_future(FutureFactor):
    data_type = 'Future'
    days_past = 5
    data_dict = dict()
    instrument_type = 'recent'
    # data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low']}
    normalize_size = 1
    normalize_type = 'ts_rank'
#    num_range = '(-0.5,1]'
    
    def calculate(self, data):
        future_close = data['close_cont_IC'].values[-1140:]
        future_high = data['high_cont_IC'].values[-1140:]
        future_low = data['low_cont_IC'].values[-1140:]
        N = 45
        bull_power = future_high - ts_truncated_ema(future_close, d=60, alpha=(N-1)/(N+1))
        bear_power = future_low - ts_truncated_ema(future_close, d=60, alpha=(N-1)/(N+1))
        factor_mean = -ts_mean(bull_power + bear_power, 180)
        factor_raw = ts_rank(factor_mean, 900)
        return factor_raw[-1]

##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

def calc_ts_pct(ts,ts_pct_win=20,min_pct=0.9,force_range=False):
    min_win = int(min_pct*ts_pct_win)
    ts_pct = bk.move_rank(ts,ts_pct_win,min_win,axis=0)
    if force_range:
        ts_pct = (ts_pct + 1)/2
    return ts_pct

def calc_ma_helper(score_raw,ma_win,ts_pct_win,min_pct=0.9):
    score_ma_raw = bk.move_mean(score_raw, ma_win, int(min_pct*ma_win), axis = 0)
    score_ma = calc_ts_pct(score_ma_raw,ts_pct_win)
    return score_ma


class csv_disp_chg_zsj(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['close', 'adjfactor'] 
    normalize_size = 1200
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        stk_close = data['close_preadj'][-1500:]
        stk_ret = (stk_close / stk_close.shift(1) - 1)

        csv_disp = stk_ret.std(axis=1)
        stk2idx_ret = stk_ret.mean(axis=1)
        csv_disp_sign_raw = csv_disp * np.sign(stk2idx_ret)
        
        csv_disp_sign = calc_ma_helper(csv_disp_sign_raw, 60, 1200)[-240:]
        flong = np.nanmean(csv_disp_sign)
        fshort = np.nanmean(csv_disp_sign[-20:])
        factor = fshort - flong
        
        return factor
##########
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_cc import *
from future_factor import FutureFactor


def r(data, x=np.nan):

    data[abs(data) < 1e-8] = x
    return data

    
class Short_BS_8_CC(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'BuyTradeNum', 'SellUniqueOrderNum', 'SellTradeNum']
    normalize_size = 1800 
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False

    def calculate(self, data):
        stk_BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-70:]
        stk_BuyTradeNum = data['BuyTradeNum'].values[-70:]
        stk_SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-70:]
        stk_SellTradeNum = data['SellTradeNum'].values[-70:]
        
        a = stk_BuyUniqueOrderNum / r(stk_BuyTradeNum)
        b = stk_SellUniqueOrderNum / r(stk_SellTradeNum)
        temp1 = (bk.move_max(a, 60, 15, axis=0) - a) / (bk.move_max(a, 60, 15, axis=0) - bk.move_min(a, 60, 15, axis=0))
        temp2 = (a - bk.move_min(a, 60, 15, axis=0)) / (bk.move_max(a, 60, 15, axis=0) - bk.move_min(a, 60, 15, axis=0))
        temp3 = (bk.move_max(b, 60, 15, axis=0) - b) / (bk.move_max(b, 60, 15, axis=0) - bk.move_min(b, 60, 15, axis=0))
        temp4 = (b - bk.move_min(b, 60, 15, axis=0)) / (bk.move_max(b, 60, 15, axis=0) - bk.move_min(b, 60, 15, axis=0))
        factor = temp2 - temp1 + temp3 - temp4
        factor = np.nanmean(factor, axis=1)
        factor = -bk.move_mean(factor, 10, 5)
        return factor[-1]
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_ts44_future_vr(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'volume', 'adjfactor', 'stk_volatility'] 
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, df):
        volume = df['volume_preadj'][-145:]
        close = df['close_preadj'][-145:]
        temp1 = volume.copy(deep = True)
        con2 = close < close.shift(1)
        temp1[con2] = -1 * volume
        
        factor = bk.move_sum(temp1, 20, 10, axis = 0)[-125:]
        factor = bk.move_mean(factor, 20, 10, axis = 0)[-105:]

        vr = (2 * df['stk_volatility'][-105:].rank(axis=1, pct=True) - 1).values
        factor = factor * vr
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 100, 50, axis = 0)[-5:]
        factor = np.nanmean(factor)
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:04:57 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


#
class cmh_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 10
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','high','adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.5, 1]'# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
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

##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

def get_norm(fa):
    fmax = np.nanmax(fa)
    fmin = np.nanmin(fa)
    divisor = fmax - fmin
    if divisor < 1e-8:
        divisior = np.nan
    return ((fa[-1] - fmin)/ divisor) * 2 - 1

class wyc_ts225_future(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IH':['close']}
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 
    
    def calculate(self, df):
        cih = df['close_cont_IH'][-1310:].values
        cih[abs(cih) < 1e-8] = np.nan
        factor = bk.move_mean(cih, 20, 10, axis = 0)[-1290:] / cih[-1290:]
        factor = bk.move_rank(factor, 20, 10, axis = 0)[-1270:]
        factor = bk.move_mean(factor, 60, 30, axis = 0)[-1210:]
        factor = get_norm(factor)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:48:18 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


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
    
##########
import numpy as np
import bottleneck as bk
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class stk2idx_ret_ch_corr_zsj(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'close', 'adjfactor', 'high']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-32:]
        stk_close = data['close_preadj'].values[-32:]
        stk_high = data['high_preadj'].values[-32:]
        stk_ret_high = ts_pct_change(stk_high, 1)
        stk_ret_close = ts_pct_change(stk_close, 1)
        ret_close_high_corr_raw = pairwise_corr_np(stk_ret_high, stk_ret_close, axis=1)
        factor_raw = bk.move_mean(ret_close_high_corr_raw, 30, 27)
        return factor_raw[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:08:12 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:07:53 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


        
class vol_diff_zsj(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close','volume']
    normalize_size = 242*5 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.85, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
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
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc12_cfg_cs(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['stk_index_corr_zz500', 'close', 'high', 'low', 'open', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-33:]
        stk_high = data['high_preadj'].values[-33:]
        stk_low = data['low_preadj'].values[-33:]
        stk_open = data['open_preadj'].values[-33:]
        stk_index_corr = data['stk_index_corr_zz500'].iloc[-33:]
        stk_price = (stk_high + stk_low + stk_open + stk_close) / 4
        n = 30
        rpp = ts_sum(stk_price, n)
        high_n = ts_max(stk_high, n)
        low_n = ts_min(stk_low, n)
        temp = replace_zero(high_n - low_n)
        arpp = (rpp - low_n) / temp
        factor_raw = np.nansum(-arpp * stk_index_corr, axis=1)
        factor_mean = ts_mean(factor_raw, 3)
        return factor_mean[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:07:10 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd



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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:52:44 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class CFG26_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 10
    data_dict = dict()
    data_dict['Stock'] = ['close','adjfactor', 'amount']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 242*3 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[-0.5, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
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

##########
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_cc import *
from operators_wsc_1_0 import ts_pct_change
from future_factor import FutureFactor


class Short_updown_cfg2_CC(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['amount', 'close', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        stk_close = data['close_preadj'].values[-150:]
        stk_amount = data['amount'].values[-150:]
        
        df_s = bk.move_sum(stk_amount, 120, 15, axis=0)
        amount_mask = np.nanquantile(df_s, 0.9, axis=1)
        amount_mask = np.expand_dims(amount_mask, axis=-1)
        amount_after_mask = (df_s > amount_mask)
        hclose = ts_pct_change(stk_close, 1)
        up_close = ma.array(amount_after_mask, mask=(hclose<=0))
        up_close = np.nansum(up_close, axis=1)
        down_close = ma.array(amount_after_mask, mask=(hclose>=0))
        down_close = np.nansum(down_close, axis=1)
        vwtc_r = (up_close - down_close) / (up_close + down_close)
        vwtc_r = bk.move_mean(vwtc_r, 30, 5)
        return vwtc_r[-1]
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:33:09 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd



class RolTrendLS_ind_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
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
    
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

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

class wyc_ts37_spot(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 5 * 242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 

    def calculate(self, df):
        close = df['close_000905.SH'][-205:]
        
        cmcs = bk.move_mean(close,25,12,axis = 0)
        cmcs[abs(cmcs) < 1e-6] = np.nan
        temp = (close - cmcs)/cmcs
        factor = temp - temp.shift(6)
        factor = -1 * ts_truncated_ema(factor[-180:], 100, 5/12).values[-80:]

        factor = bk.move_rank(factor, 25, 12, axis = 0)[-55:]
        factor = bk.move_mean(factor, 50, 25, axis = 0)[-5:]

        factor = np.nanmean(factor)

        return factor
    
##########
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_gp4_future(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    # data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Continuous_Data'] = {'IC':['amount']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        future_amount = data['amount_cont_IC'].values[-103:]
        amount_max = ts_max(future_amount, 39)
        factor_raw = ts_pred(amount_max, 64)
        return factor_raw[-1]
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:49:36 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class CFG20_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 10
    data_dict = dict()
    data_dict['Stock'] = ['high','low','close','weight', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[0, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:26:01 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class LminLmean_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':[ 'low']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '(-0.5, 1]'
    instrument_type='recent'
    
    def calculate(self, data):


        low = data['low_cont_IC'].values[-60:]
        temp1 = np.nanmin(low)
        temp2 = np.nanmean(low[-30:])
        factor = -temp1/temp2
        return factor
##########
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_gp6_future(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    # data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Continuous_Data'] = {'IC':['volume']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        future_volume = data['volume_cont_IC'].iloc[-22:]
        factor_raw = ts_std(future_volume, 22)
        return factor_raw[-1]
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk

def get_norm(fa):
    fmax = np.nanmax(fa)
    fmin = np.nanmin(fa)
    divisor = fmax - fmin
    if divisor < 1e-8:
        divisior = np.nan
    return ((fa[-1] - fmin)/ divisor) * 2 - 1

def get_delta(data, n):
    return data[n:] - data[:-n]

class wyc_ts2_future(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close','volume']} 
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 

    def calculate(self, df):
        volume = df['volume_cont_IC'].values[-5*242 - 17:]
        close = df['close_cont_IC'].values[-5*242 - 17:]
        dev = get_delta(volume, 5)
        dev[dev > 0] = 1
        dev[dev < 0] = -1
        factor = -1 * dev * get_delta(close, 5)
        
        factor = bk.move_mean(factor,2,1,axis = 0)
        factor = bk.move_mean(factor,10,5,axis = 0)
        factor = get_norm(factor[-5*242:])
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 10:51:09 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from operators_cc import *
import pandas as pd

class HDLD_CFG2_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 9
    data_dict = dict()
    data_dict['Stock'] = [ 'amount', 'weight', 'close','low','high', 'open', 'adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.5, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):

        index_close = data['close_000905.SH'].iloc[-2001:]
        stk_close = data['close_preadj'].iloc[-2001:]
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = (stk_ret.rolling(1200, min_periods=600).corr(index_ret.iloc[:,0])).iloc[-800:]
        
        stk_index_corr = (stk_index_corr.replace([-np.inf, np.inf], np.nan))
        stk_index_corr = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0)
        bool_df = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0)
        
        hclose = data['close_preadj'].iloc[-830:].values
        hopen = data['open_preadj'].iloc[-830:].values
        
        hlow = data['low_preadj'].iloc[-830:].values
        hhigh = data['high_preadj'].iloc[-830:].values
        
        temp = np.abs(hclose-hopen)
        temp[temp==0] = 0.01
        
        temp0 = (hhigh - hlow)
        temp1 = (temp0/temp)[-800:]
        a = bk.move_sum((hclose[1:]/hclose[:-1]-1), 30, min_count = 15, axis = 0)[-800:]
        vwtc_r = (temp1*(a))
        vwtc_r = pd.DataFrame(vwtc_r, index = bool_df.index, columns = bool_df.columns)

        factor = np.nanmean(vwtc_r[bool_df], axis = 1)
        
        factor = bk.move_mean(factor,10,  min_count = 5, axis = 0)
        #print(b.iloc[:, 0].corr(b1.iloc[:, 0]))
        factor2 = rolling_norm(factor, 242*3, method = 'ts_rank')
        factor2 = np.nanmean(factor2[-3:])

        return factor2
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_cfg4(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'weight', 'high', 'low', 'open', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-65:]
        stk_open = data['open_preadj'].values[-65:]
        stk_high = data['high_preadj'].values[-65:]
        stk_low = data['low_preadj'].values[-65:]
        stk_weight = data['weight'].values[-65:]
        a = stk_high - stk_low
        a[a<1e-5] = np.nan
        b = stk_close - stk_open
        b[b<0] = np.nan
        c = ts_sum(b/a, 60)
        factor_raw = np.nansum(c * stk_weight, axis=1)
        factor_raw = ts_mean(factor_raw, 5)
        return factor_raw[-1]
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:31:23 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class OCtHL_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':[ 'close','low','high', 'open']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    instrument_type='recent'
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

##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc5_cfg_ws(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'weight', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'rolling_norm'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-121:]
        stk_weight = data['weight'].values[-121:]
        n = 20
        m = int(n/2) + 1
        close_ma = ts_mean(stk_close, n)
        dev = stk_close - close_ma
        devpos = dev.copy()
        devneg = -dev.copy()
        devpos[devpos<0] = 0
        devneg[devneg<0] = 0
        sumpos = ts_sum(devpos, m)
        sumneg = ts_sum(devneg, m)
        temp = replace_zero(sumpos + sumneg)
        tii = sumpos / temp
        factor_raw = np.nansum(tii * stk_weight, axis=1)
        factor_mean = ts_mean(factor_raw, 90)
        return factor_mean[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:53:55 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class CFG9_CC(FutureFactor):

    
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [ 'volume', 'close', 'adjfactor']
    #data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(0, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
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
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc20_cfg_vr(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Stock'] = ['close', 'stk_volatility', 'adjfactor']
    normalize_size = 2400
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-60:]
        spot_close = data['close_000905.SH'].values[-60:]
        stk_volatility = data['stk_volatility'].values[-60:]
        stk_volatility_rank_mask = section_rank_np(stk_volatility, pct=True) * 2 - 1
        stk_ret = ts_pct_change(stk_close, 45)
        spot_ret = ts_pct_change(spot_close, 45)
        excess_ret = stk_ret - spot_ret
        stk_volatility_rank_mask[np.isnan(excess_ret)] = np.nan
        stk_volatility_rank_mask[excess_ret >= 0] = 0
        factor_raw = np.nansum(stk_volatility_rank_mask, axis=1)
        factor_mean = -ts_mean(factor_raw, 15)
        return factor_mean[-1]

##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

class PositiontoVolume_CC(FutureFactor):

    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['OpenInterest','volume']} 
    normalize_size = 1200
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    handle_preadj = None 
    
    def calculate(self, data):
        a = data['volume_cont_IC'][-41:].rolling(40, min_periods = 30).std()
        a[abs(a) < 1e-8] = np.nan
        pd_r = -1 * data['OpenInterest_cont_IC'][-41:]/ a
        factor = pd_r.values[-1]
        return factor
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc_ti10_cfg(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'open', 'high', 'weight', 'adjfactor']
    normalize_size = 600
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-60:]
        stk_open = data['open_preadj'].values[-60:]
        stk_high = data['high_preadj'].values[-60:]
        stk_weight = data['weight'].values[-60:]
        x = stk_close - stk_open
        y = stk_open.copy()
        y = np.where(x>0, stk_close, y)
        z = replace_zero(stk_high - y)
        u = x / z
        factor_init = np.nansum(u * stk_weight, axis=1)
        factor_raw = ts_mean(factor_init, 60)
        return factor_raw[-1]
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc15_cfg_cr(FutureFactor):
    data_type = 'IndexStock'
    days_past = 2
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'stk_index_corr_zz500', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '(-0.3,1]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-256:]
        stk_index_corr = data['stk_index_corr_zz500'].values[-256:]
        stk_index_corr_rank_mask = section_rank_np(stk_index_corr, pct=True) * 2 - 1
        n = 10
        temp = ts_sum(abs(ts_delta(stk_close, 1)), n)
        vi = abs(ts_delta(stk_close, n)) / replace_zero(temp)
        vidya = vi * stk_close + (1-vi) * ts_delay(stk_close, 1)
        factor_init = rolling_norm(vidya, 240)
        factor_raw = np.nansum(factor_init * stk_index_corr_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 2)
        return factor_mean[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:01:37 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class LMLS_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','low', 'adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}
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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:04:40 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


#
class ZHZH_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['amount', 'high', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀

    def calculate(self, data):
        

        hamount = data['amount'].iloc[-120:]
        hhigh = data['high_preadj'].iloc[-75:].values      

        df_s = hamount.sum(axis = 0).astype(float)
        bool_df = df_s.gt(df_s.quantile(0.90))

        
        a = (hhigh>=(bk.move_max(hhigh, 30, min_count = 5, axis = 0)))
        temp = np.nanmean(a[-40:], axis = 0)
        #temp = temp.iloc[-1]
        #temp = np.nanmean(((hhigh>=(bk.move_mean(hhigh, 30, min_count = 5, axis = 0))))[-40:], axis = 0)
        temp = np.nanmean(temp*bool_df)
        
        return temp
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class xdy_ts1_spot(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close','high']}
    normalize_size = 5 * 242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.5,1]'
    handle_preadj = None 
    
    def calculate(self, df):
        high = df['high_000905.SH'][-80:].values
        close = df['close_000905.SH'][-80:].values
        high[abs(high) < 1e-8] = np.nan
        gain_high_60 = (high[60:] / high[:-60] - 1)[-20:]
        h_c = (close / high - 1)
        a = bk.move_mean(h_c, 60, 30, axis = 0)[-20:]
        a[abs(a) < 1e-8] = np.nan
        factor = bk.move_sum(gain_high_60 / a, 10, 5, axis = 0)[-10:]
        factor = np.nanmean(factor) * -1
        return factor

##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class dpo_std_zsj(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close']}
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.5,1]'
    handle_preadj = None 

    def calculate(self, data):
        close = data[['close_cont_IC']][-1298:]
        mma = bk.move_mean(close, 45, 22, axis = 0)[45:]
        dpo_raw = close[68:] - mma[:-23]
        dpo_std_raw = bk.move_std(dpo_raw, 30, 1, axis = 0)[-1200:]
        factor = bk.move_rank(dpo_std_raw, 1200, 1080, axis = 0)[-1]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:05:21 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd
  
class ClMaxClMin_ind_CC(FutureFactor):

    data_type = 'Future'
    days_past = 1
    instrument_type='recent'
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']} 
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    num_range = None
    instrument_type='recent'
    
    def calculate(self, data):
        
        hclose = data['close_000905.SH'].values[-60:]
        
        factor = np.nanmax(hclose)/np.nanmin(hclose)
        
        return factor

##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd


class wyc_ts14_spot(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 0
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 

    def calculate(self, df):
        close = df['close_000905.SH'][-1403:]
        factor = np.where(close > close.shift(1), close.rolling(50, min_periods=25).std(), 0)[-1353:]
        factor = ((bk.move_rank(factor, 120, 60, axis = 0) + 1) / 2)[-1233:]
        factor = bk.move_mean(factor, 20, 10, axis = 0)[-1213:]
 
        factor = bk.move_rank(factor, 1210, 605, axis = 0)[-3:]
        factor = np.nanmean(factor)

        return factor
##########
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class stk2idx_amt_chg_u2d_zsj(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'close', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-62:]
        stk_close = data['close_preadj'].values[-62:]
        stk_amt_chg = ts_delta(stk_amount, 1)
        stk_ret = ts_pct_change(stk_close, 1)
        active_raw = ma.array(stk_amt_chg, mask=(stk_ret<=0))
        inactive_raw = ma.array(stk_amt_chg, mask=(stk_ret>=0))
        score = np.nanmean(active_raw, axis=1) - np.nanmean(inactive_raw, axis=1)
        factor_raw = bk.move_mean(score, 60, 54)
        return factor_raw[-1]
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero, replace_inf



class wsc3_cfg_vr(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Stock'] = ['close', 'stk_volatility', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].iloc[-118:]
        stk_volatility = data['stk_volatility'].values[-118:]
        spot_close = data['close_000905.SH'].iloc[-118:]
        stk_volatility_rank_mask = 2 * section_rank_np(stk_volatility, pct=True) - 1
        spot_ret = ts_pct_change(spot_close, 3)
        stk_ret = ts_pct_change(stk_close, 3)
        ret_diff = stk_ret.sub(spot_ret.iloc[:,0], axis=0)
        ret_diff[ret_diff > 0] = 1
        ret_diff[ret_diff <= 0] = 0
        ret_diff = ret_diff.values
        temp = replace_zero(ts_sum(ret_diff, 90))
        factor_init = replace_inf(ts_sum(ret_diff, 15) / temp)
        factor_raw = np.nansum(factor_init * stk_volatility_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 25)
        return factor_mean[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:32:48 2021

@author: appadmin
"""


import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class Rev_ind_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}  
    normalize_size = 4800
    normalize_type = 'rolling_norm'
#    num_range = '[-1, 1]'
    
    def calculate(self, data):
        hclose = data['close_000905.SH'].iloc[-150:]
        ret = (hclose.iloc[-1]/hclose.shift(120).iloc[-1]-1)

        return ret
    
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk

def get_norm(fa):
    fmax = np.nanmax(fa)
    fmin = np.nanmin(fa)
    divisor = fmax - fmin
    if divisor < 1e-8:
        divisior = np.nan
    return ((fa[-1] - fmin)/ divisor) * 2 - 1

class wyc_ifcv_corr(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['close','volume']} 
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 

    def calculate(self, df):
        volume = df['volume_cont_IF'][-5*242 - 60:]
        close = df['close_cont_IF'][-5*242 - 60:]
        s = volume.rolling(30, min_periods=15).std()
        f = close.rolling(30, min_periods=15).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        factor = volume.rolling(30, min_periods=15).cov(close) / (s * f)
        factor = -1 * bk.move_mean(factor.values, 30, 15, axis = 0)
        factor = get_norm(factor[-5*242:])
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:01:57 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class LSC_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 8
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','low', 'high', 'adjfactor', 'amount']
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
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_1_cfg(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'weight', 'amount', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-45:]
        stk_weight = data['weight'].values[-45:]
        stk_amount = data['amount'].values[-45:]
        stk_ret = ts_pct_change(stk_close, 1)
        log_ret = log(stk_ret + 1)
        ret_std = ts_std(stk_ret, 15)
        log_ret_weight = log_ret * stk_amount * ret_std
        factor_raw = np.nansum(ts_sum(log_ret_weight, 30)*stk_weight, axis=1)
        return factor_raw[-1]
##########
import bottleneck as bk
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class ma_displaced_std_zsj(FutureFactor):
    data_type = 'Future'
    days_past = 6
    data_dict = dict()
    instrument_type = 'recent'
    # data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Continuous_Data'] = {'IC':['close']}
    normalize_size = 1
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        future_close = data['close_cont_IC'].values[-1351:]
        ma_close = bk.move_mean(future_close, 90, 1)
        ma_displaced = ts_delay(ma_close, 10)
        ma_diff = future_close - ma_displaced
        score_raw = bk.move_std(ma_diff, 40, 36)
        ma_displaced_std = bk.move_rank(score_raw, 1210, int(1210*0.9))
        return ma_displaced_std[-1]

##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

def rolling_norm(sig, window=1200, method='max_min'):
    assert isinstance(sig, pd.Series) or isinstance(sig, pd.DataFrame) or isinstance(sig, np.ndarray), 'input must be a series, dataframe or ndarray'
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
            elif isinstance(sig, np.ndarray):
                sig_max = bk.move_max(sig, window=window, min_count=int(window / 2), axis=0)
                sig_min = bk.move_min(sig, window=window, min_count=int(window / 2), axis=0)
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
            elif isinstance(sig, np.ndarray):
                output = bk.move_rank(sig, window=d, min_count=int(d / 2), axis=0)
            return signal
        
        
class xdy_ts13_spot(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 4
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['high']}
    normalize_size = 5*242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[0,1]'
    handle_preadj = True
    
    def calculate(self, df):
        high = df['high_000905.SH'][-881:].values
        factor = bk.move_max(high, 121, 60, axis = 0)[-760:]
        factor = rolling_norm(factor, 3*242)[-34:]
        factor = factor[15:] - factor[:-15]
        factor = np.nanmax(factor)

        return factor

##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

def ts_position(x, t):
    def get_position(ylist):
        smin = min(ylist)
        smax = max(ylist)
        y = ylist[-1]
        return (y - smin) / (smax - smin)
    return x.rolling(t, min_periods = t // 2).apply(get_position)

class xdy_ts4_spot(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['high']}
    normalize_size = 1210
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    handle_preadj = None 
    
    def calculate(self, df):
        high = df['high_000905.SH'][-130:]
        factor = ts_position(high, 30)
        factor = -1 * factor.rolling(100, min_periods=20).skew()
        return factor.values[-1]
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:09:56 2021

@author: appadmin
"""

from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class HLTM_IFIC_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['high','low', 'vwap']} 
    normalize_size = 1200
    normalize_type = 'ts_rank'
    instrument_type='recent'
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

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:34:59 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class fvs2_ind_IFIC_CC(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    data_dict['Continuous_Data'] = {'IF':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    instrument_type='recent'
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
    
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero


    
class wsc_hf18(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['Bid1AmtMean', 'Buy1NumOrdersMean', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        stk_weight = data['weight'].values[-15:]
        stk_Bid1AmtMean = data['Bid1AmtMean'].values[-15:]
        stk_Buy1NumOrdersMean = data['Buy1NumOrdersMean'].values[-15:]
        factor_init = np.nansum(stk_Bid1AmtMean / replace_zero(stk_Buy1NumOrdersMean) * stk_weight, axis=1)
        factor_raw = ts_mean(factor_init, 15)
        return factor_raw[-1]
##########
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_cc import *
from future_factor import FutureFactor


def r(data, x=np.nan):

    data[abs(data) < 1e-8] = x
    return data

    
class Short_BS9_CC(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['amount', 'buy_superorder_count', 'buy_bigorder_count', 'buy_midorder_count', 'buy_smallorder_count']
    normalize_size = 1200 
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False

    def calculate(self, data):
        stk_amount = data['amount'].values[-65:]
        stk_buy_superorder_count = data['buy_superorder_count'].fillna(0).values[-65:]
        stk_buy_bigorder_count = data['buy_bigorder_count'].fillna(0).values[-65:]
        stk_buy_midorder_count = data['buy_midorder_count'].fillna(0).values[-65:]
        stk_buy_smallorder_count = data['buy_smallorder_count'].fillna(0).values[-65:]

        amount_sum = bk.move_sum(stk_amount, window=60, min_count=15, axis=0)
        amount_mask = np.nanquantile(amount_sum, 0.9, axis=1)
        amount_mask = np.expand_dims(amount_mask, axis=-1)
        alll = r(stk_buy_superorder_count + stk_buy_bigorder_count + stk_buy_midorder_count + stk_buy_smallorder_count)
        temp2 = (stk_buy_superorder_count + stk_buy_bigorder_count) / alll
        temp2_after_mask = ma.array(temp2, mask=(amount_sum<=amount_mask))
        factor_raw = np.nanmean(temp2_after_mask, axis=1)
        factor_mean = bk.move_mean(factor_raw, window=5, min_count=1, axis=0)
        return factor_mean[-1]
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

def get_norm(fa):
    fmax = np.nanmax(fa)
    fmin = np.nanmin(fa)
    divisor = fmax - fmin
    if divisor < 1e-8:
        divisior = np.nan
    return ((fa[-1] - fmin)/ divisor) * 2 - 1

def rolling_norm(sig, window=1200, method='max_min'):
    assert isinstance(sig, pd.Series) or isinstance(sig, pd.DataFrame) or isinstance(sig, np.ndarray), 'input must be a series, dataframe or ndarray'
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
            elif isinstance(sig, np.ndarray):
                sig_max = bk.move_max(sig, window=window, min_count=int(window / 2), axis=0)
                sig_min = bk.move_min(sig, window=window, min_count=int(window / 2), axis=0)
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
            elif isinstance(sig, np.ndarray):
                output = bk.move_rank(sig, window=d, min_count=int(d / 2), axis=0)
            return signal
        
        
class xdy_ts13_future(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 9
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['high']} 
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[0,1]'
    handle_preadj = None
    
    def calculate(self, df):
        high = df['high_cont_IC'][-2091:].values
        factor = bk.move_max(high, 121, 60, axis = 0)[-1970:]
        factor = rolling_norm(factor, 3*242)[-1244:]
        factor = factor[15:] - factor[:-15]
        factor = bk.move_max(factor, 19, 9, axis = 0)[-1210:]
        factor = get_norm(factor)
        return factor
    
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd
from joblib import Parallel, delayed

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
    assert isinstance(df, pd.DataFrame), 'the data structure of input is illegal, must be dataframe'
    results = Parallel(n_jobs=n_jobs)(delayed(func)(df[i], **kwargs) for i in df.columns)
    results_df = pd.DataFrame(results, index=df.columns, columns=df.index)
    return results_df.T

class wyc_ts6_future_ar(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['close', 'amount', 'high', 'low', 'volume', 'adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[0,1]'
    handle_preadj = True 

    def calculate(self, df):
        a = df['high_preadj'][-1535:] - df['low_preadj'][-1535:]
        a[abs(a) < 1e-8] = np.nan
        factor = df['volume_preadj'][-1535:] * ((df['close_preadj'][-1535:] - df['low_preadj'][-1535:]) - (df['high_preadj'][-1535:] - df['close_preadj'][-1535:])) / a
        factor = multi_processing_joblib(df=factor, func=ts_truncated_ema, n_jobs=-1, d=200, alpha= 1/45).values[-1335:]
        factor = bk.move_rank(factor, 1200, 600, axis = 0)[-135:]
        factor = bk.move_mean(factor, 15, 7, axis = 0)[-120:]

        a = df['amount'][-120:]
        ar = (2 * a.rank(axis=1, pct=True) - 1).values
        
        factor = factor * ar
        factor = np.nansum(factor,axis=1)

        factor = bk.move_rank(factor, 100, 50, axis = 0)[-20:]
        factor = np.nanmean(factor)

        return factor
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from future_factor import FutureFactor

def get_norm(fa):
    fmax = np.nanmax(fa)
    fmin = np.nanmin(fa)
    divisor = fmax - fmin
    if divisor < 1e-8:
        divisior = np.nan
    return ((fa[-1] - fmin)/ divisor) * 2 - 1

class ts29_futures_zf(FutureFactor):
    '''
    期货类因子
    '''
    data_type = 'Future' # 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    instrument_type = 'recent' # 期货连续合约数据种类, 近月数据为'recent', 主力为'main'
    data_dict['Continuous_Data'] = {'IC':['close','volume']} #期货连续合约，处理了合约跳变问题
    normalize_size = 0 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'

    def calculate(self, data):
        close = data['close_cont_IC'].values[-1440:]
        volume = data['volume_cont_IC'].values[-1440:]
            
        fac = -1*(close[10:]-close[:-10])/close[:-10]*volume[10:]
        fac = (bk.move_rank(fac,window = 20, min_count = 10)[-1410:]+1)/2
        fac = bk.move_mean(fac,200,100,axis = 0)[-1210:]
        return get_norm(fac)
##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

def section_rank_np(data, pct=False):
    # 基于numpy的截面排序，对应df.rank(method='first')
    if not isinstance(data, np.ndarray):
        raise TypeError('Only supports the following type: np.ndarray')
    data_argsort = bk.rankdata(data, axis = 1)  # +1是因为numpy从0计数，pandas从1计数
    data_argsort[np.isnan(data)] = np.nan  # numpy argsort会让nan也参与排序，但是pandas不会，所以把这些值重新置为nan
    if pct == True:
        data_argsort = data_argsort / (~np.isnan(data)).sum(axis=1, keepdims=True)
    return data_argsort
def ts_std(df1, d):
    # moving time-series rank for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                           index=df1.index, name=df1.name)
    return output
class LminC_ind_CC_vr_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'low', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        stk_close = data['close_preadj'][-216:].values
        stk_ret = stk_close[1:] / stk_close[:-1] - 1
        stk_volatility = bk.move_std(stk_ret, window = 30, min_count = 15, axis=0)
        
        mask = 2 * section_rank_np(stk_volatility, pct = True)[-185:] - 1
        lltc_ind_r = -1 * bk.move_min(data['low_preadj'][-185:].values, 180, min_count=90, axis = 0) / data['close_preadj'][-185:].values
        factor = np.nansum(lltc_ind_r*mask, axis = 1)[-5:]
        factor = np.nanmean(factor)
        return factor 
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

def rolling_norm(sig, window=1200, method='max_min'):
    assert isinstance(sig, pd.Series) or isinstance(sig, pd.DataFrame) or isinstance(sig, np.ndarray), 'input must be a series, dataframe or ndarray'
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
            elif isinstance(sig, np.ndarray):
                sig_max = bk.move_max(sig, window=window, min_count=int(window / 2), axis=0)
                sig_min = bk.move_min(sig, window=window, min_count=int(window / 2), axis=0)
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
            elif isinstance(sig, np.ndarray):
                output = bk.move_rank(sig, window=d, min_count=int(d / 2), axis=0)
            return signal
        
        
class xdy_ts13_future_nr_as_50_10(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 10
    data_dict = dict()
    data_dict['Stock'] = ['high','amount','adjfactor']
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[0,1]'
    handle_preadj = True
    
    def calculate(self, df):
        high = df['high_preadj'][-2150:].values
        factor = bk.move_max(high, 121, 60, axis = 0)[-2030:]
        factor = rolling_norm(factor, 3*242)[-1304:]
        factor = factor[15:] - factor[:-15]
        factor = bk.move_max(factor, 19, 9, axis = 0)[-1270:]
        
        factor = rolling_norm(factor, 5 * 242)[-60:]

        a = df['amount'][-60:].values
        factor = factor * a
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 50, 25, axis = 0)[-10:]
        factor = np.nanmean(factor)
        
        return factor
    
##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd
import datetime

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

        hhigh = data['high_preadj'].iloc[-61:]
        hclose = data['close_preadj'].iloc[-61:]
        hweight = data['weight'].iloc[-1:]
        s = hhigh.rolling(60, min_periods=30).std()
        f = hclose.rolling(60, min_periods=30).std()
        s[abs(s) < 1e-7] = np.nan
        f[abs(f) < 1e-7] = np.nan
        t_pcor2 = hhigh.rolling(60, min_periods=30).cov(hclose) / (s * f)

        t_pcor2[~np.isfinite(t_pcor2)] = 0
        
        factor = np.nanmean(t_pcor2.iloc[-1:]*hweight)
        return factor
##########
import numpy as np
from operators_wsc_1_0 import *
from future_factor import FutureFactor



class wyc_ts5_future_nr_as_fast(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'amount', 'adjfactor']
    normalize_size = 237 * 5
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-91:]
        stk_amount = data['amount'].values[-91:]
        
        N = 45
        temp1 = ts_delta(ts_sum(stk_close, N) / N, N) / ts_delay(stk_close, N)
        temp2 = stk_close - ts_min(stk_close, N)
        temp3 = ts_delta(stk_close, 3)
        factor_raw = np.where(temp1<=0.05, temp2, temp3)
        factor_raw = np.nansum(factor_raw * stk_amount, axis=1)
        return factor_raw[-1]
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

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

class xdy_ts2_spot(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 2
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['high','low']} 
    normalize_size = 5*242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.3,1]'
    handle_preadj = None
    
    def calculate(self, df):
        high = df['high_000905.SH'][-120:]
        low = df['low_000905.SH'][-120:]
        high[abs(high) < 1e-8] = np.nan
        gain_high_20 = high / high.shift(20) - 1
        factor = (low * gain_high_20).to_frame()[-100:]
        factor = ts_truncated_ema(factor, 100, 1/26).values[-1]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:58:37 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:32:06 2021

@author: appadmin
"""


import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class PositiontoVolume2_IFIC_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':[ 'OpenInterest', 'volume']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    instrument_type='recent'
    #num_range = [-0.499999, 1]
    
    def calculate(self, data):

        a = (data['OpenInterest_cont_IF'].values)[-20:]
        a[abs(a) < 1e-8] = np.nan
        hvolume = (data['volume_cont_IF'].values[-20:])
        temp = hvolume/a
        factor = np.nanmean(temp)
        return factor
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc5_cfg_cr(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'stk_index_corr_zz500', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '(-0.8,1]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-56:]
        stk_index_corr = data['stk_index_corr_zz500'].values[-56:]
        stk_index_corr_rank_mask = 2 * section_rank_np(stk_index_corr, pct=True) - 1
        n = 20
        m = int(n/2) + 1
        close_ma = ts_mean(stk_close, n)
        dev = stk_close - close_ma
        devpos = dev.copy()
        devneg = -dev.copy()
        devpos[devpos<0] = 0
        devneg[devneg<0] = 0
        sumpos = ts_sum(devpos, m)
        sumneg = ts_sum(devneg, m)
        temp = replace_zero(sumpos + sumneg)
        tii = sumpos / temp
        factor_raw = np.nansum(tii * stk_index_corr_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 25)
        return factor_mean[-1]

##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk

# rolling norm前有fillna
class wyc_ts44_spot(FutureFactor):
    data_type = 'Future' 
#     instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close','volume']} 
    normalize_size = 5 * 242 
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 

    def calculate(self, df):
        
        v = df['volume_000905.SH'][-40:]
        temp1 = v
        c = df['close_000905.SH'][-40:]
        con2 = c < c.shift(1)
        temp1[con2] = -1 * temp1
        
        factor = bk.move_sum(temp1.values, window=20, min_count=int(20 / 2), axis=0)[-20:]
        factor = np.nanmean(factor)

        return factor

##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

        
class xdy_ts6_spot_tr(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = ['close','turnover_rate','adjfactor']
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[-1,0.2]'
    handle_preadj = True
    
    def calculate(self, df):
        close = df['close_preadj'][-365:].values
        gain_close_30 = close[30:]/close[:-30] - 1
        factor = 2 * gain_close_30[20:] - gain_close_30[:-20]
        factor = bk.move_mean(factor, 110, 55, axis = 0)[-205:]
       
        t = df['turnover_rate'][-205:]
        tr = (2 * t.rank(axis=1, pct=True) - 1).values
        factor = factor * tr
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 200, 100, axis = 0)[-5:]
        factor = np.nanmean(factor)

        return factor

##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc2_cfg_cr(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'stk_index_corr_zz500', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '(-0.9,1]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-48:]
        stk_index_corr = data['stk_index_corr_zz500'].values[-48:]
        corr_rank_mask  = 2 * section_rank_np(stk_index_corr, pct=True) - 1
        stk_ret = ts_pct_change(stk_close, 3)
        ret_mean_plus_std = ts_mean(stk_ret, 30) + 0.5 * ts_std(stk_ret, 30)
        factor_init = np.nansum(ret_mean_plus_std * corr_rank_mask, axis=1)
        factor_raw = ts_mean(factor_init, 15)
        return factor_raw[-1]
##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

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
    assert 0 < alpha < 1
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

class wyc_ts6_spot(FutureFactor):

    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 5
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close','high','low','volume']} 
    normalize_size = 5*242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    handle_preadj = None 
    
    def calculate(self, df):
        a = (df['high_000905.SH'] - df['low_000905.SH'])
        a[abs(a) < 1e-8] = np.nan
        b = df['volume_000905.SH'] * ((df['close_000905.SH'] - df['low_000905.SH']) - (df['high_000905.SH'] - df['close_000905.SH']))
        c = b / a
        factor = ts_truncated_ema(c, 800, 1/50)[-260:]
        factor = (bk.move_rank(factor.values, 100, min_count=50, axis = 0) + 1)/2
        factor = np.nanmean(factor[-160:])
        return factor
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc9_cfg_wr(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['volume', 'close', 'open', 'weight', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_open = data['open_preadj'].values[-51:]
        stk_close = data['close_preadj'].values[-51:]
        stk_volume = data['volume_preadj'].values[-51:]
        stk_weight = data['weight'].iloc[-51:]
        # weight_rank_mask = section_rank_np(stk_weight, pct=True) * 2 - 1
        weight_rank_mask = stk_weight.rank(axis=1, pct=True) * 2 - 1
        min_30_earning = (stk_close - ts_delay(stk_open, 30)) * stk_volume
        # print(min_30_earning.shape, weight_rank_mask.values.shape)
        factor_raw = np.nansum(min_30_earning * weight_rank_mask.values, axis=1)
        factor_mean = ts_mean(factor_raw, 20)
        return factor_mean[-1]

##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class xdy_ts6_spot_ar(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close','amount','adjfactor']
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, df):
        close = df['close_preadj'][-195:].values
        gain_close_30 = close[30:]/close[:-30] - 1
        factor = 2 * gain_close_30[20:] - gain_close_30[:-20]
        factor = bk.move_mean(factor, 110, 55, axis = 0)[-35:]

        a = df['amount'][-35:]
        ar = (2 * a.rank(axis=1, pct=True) - 1).values
        factor = factor * ar
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 20, 10, axis = 0)[-15:]
        factor = np.nanmean(factor)

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:02:46 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


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
##########
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_gp10_future(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    # data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Continuous_Data'] = {'IC':['amount', 'close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        future_amount = data['amount_cont_IC'].iloc[-113:]
        future_close = data['close_cont_IC'].iloc[-113:]
        amount_std = ts_std(future_amount, 44)
        close_amount_cov = ts_cov(future_amount, -future_close, 14)
        temp = ts_argmax(close_amount_cov, 97)
        factor_raw = amount_std * temp
        return factor_raw[-1]
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:47:41 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

    
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
##########
import numpy as np
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


class wsc_fast3_hf(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'BuyTradeNum', 'weight']
    normalize_size = 1200 
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False

    def calculate(self, data):
        stk_BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-4:]
        stk_BuyTradeNum = data['BuyTradeNum'].values[-4:]
        stk_weight = data['weight'].values[-4:]
        
        factor_raw = np.nansum(stk_BuyTradeNum / replace_zero(stk_BuyUniqueOrderNum) * stk_weight, axis=1)
        factor_mean = ts_mean(factor_raw, 4)
        return factor_mean[-1]
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

def rolling_norm(sig, window=1200, method='max_min'):
    assert isinstance(sig, pd.Series) or isinstance(sig, pd.DataFrame) or isinstance(sig, np.ndarray), 'input must be a series, dataframe or ndarray'
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
            elif isinstance(sig, np.ndarray):
                sig_max = bk.move_max(sig, window=window, min_count=int(window / 2), axis=0)
                sig_min = bk.move_min(sig, window=window, min_count=int(window / 2), axis=0)
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
            elif isinstance(sig, np.ndarray):
                output = bk.move_rank(sig, window=d, min_count=int(d / 2), axis=0)
            return signal

def get_delta(data, n):
    return data[n:] - data[:-n]

class wyc_ts5_future_nr_as(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 12
    data_dict = dict()
    data_dict['Stock'] = ['close','amount','adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True 

    def calculate(self, df):
        N = 45
        close = df['close_preadj'].values
        origin = get_delta((bk.move_sum(close, N,int(N/2), axis =0) / N), N) / close[:-N]
        change1 = -1 * (close - bk.move_min(close, N,int(N/2), axis =0))[N:]
        change2 = -1 * get_delta(close, 3)[N-3:]
        factor = np.where(origin<=0.05,change1,change2)[-1530 - 5*242:]

        factor = bk.move_rank(-1*factor, 1200, 600, axis = 0)[-5*242 - 330:]
        factor = bk.move_mean(factor,15,7,axis = 0)[-5*242 - 315:]

        factor = rolling_norm(factor, 5 * 242)[-315:]

        a = df['amount'].values[-315:]
        factor = factor * a
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 300, 150, axis = 0)[-15:]
        factor = np.nanmean(factor)
     
        return factor
##########
import bottleneck as bk
from future_factor import FutureFactor
from operators_wsc_1_0 import *


class retvol_zsj(FutureFactor):
    data_type = 'Future'
    days_past = 2
    data_dict = dict()
    instrument_type = 'recent'
    # data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Continuous_Data'] = {'IC':['close']}
    normalize_size = 1
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        future_close = data['close_cont_IC'].values[-302:]
        future_ret = ts_pct_change(future_close, 1)
        retvol_raw = bk.move_std(future_ret, 60, 1)
        retvol = bk.move_rank(retvol_raw, 240, int(240*0.9))
        return retvol[-1]


##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:09:08 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

    
class HL123_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['high','low']} 
    instrument_type='recent'
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '[0, 1]'
    instrument_type='recent'
    
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


##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:22:30 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


    
class HmaxC_ind_CC(FutureFactor):
  
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['high', 'low', 'close']}
    normalize_size = 1000
    normalize_type = 'ts_rank'
#    num_range = '[0, 1]'
    
    def calculate(self, data):

        hhigh = (data['high_000905.SH'].values)[-130:]
        hclose =(data['close_000905.SH'].values)[-130:]
        temp1 = -bk.move_max(hhigh, 120, min_count = 90) / hclose
        temp1[abs(temp1)>100000] = np.nan
        
        return temp1[-1]  
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc2_cfg_vs(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'stk_volatility', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-48:]
        stk_volatility_mask = data['stk_volatility'].values[-48:]
        stk_ret = ts_pct_change(stk_close, 3)
        ret_mean = ts_mean(stk_ret, 30)
        factor_init = np.nansum(ret_mean * stk_volatility_mask, axis=1)
        factor_raw = ts_mean(factor_init, 15)
        return factor_raw[-1]

##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc20_cfg_cr(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Stock'] = ['close', 'stk_index_corr_zz500', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '[0,1]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-70:]
        spot_close = data['close_000905.SH'].values[-70:]
        stk_index_corr = data['stk_index_corr_zz500'].values[-70:]
        stk_index_corr_rank_mask = section_rank_np(stk_index_corr, pct=True) * 2 - 1
        stk_ret = ts_pct_change(stk_close, 45)
        spot_ret = ts_pct_change(spot_close, 45)
        excess_ret = stk_ret - spot_ret
        stk_index_corr_rank_mask[np.isnan(excess_ret)] = np.nan
        stk_index_corr_rank_mask[excess_ret >= 0] = 0
        factor_raw = np.nansum(stk_index_corr_rank_mask, axis=1)
        factor_mean = -ts_mean(factor_raw, 25)
        return factor_mean[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:00:38 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


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
##########
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class stk2idx_ret_rank_short_a2p_zsj(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'close', 'adjfactor']
    normalize_size = 2800
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-57:]
        stk_close = data['close_preadj'].values[-57:]
        stk_ret = ts_pct_change(stk_close, 1)
        stk_ret_rank_short = bk.move_rank(stk_ret, 30, 27, axis=0)
        cut_line = np.nanmedian(stk_amount, axis=1, keepdims=True)
        active_raw = ma.array(stk_ret_rank_short, mask=(stk_amount<cut_line))
        inactive_raw = ma.array(stk_ret_rank_short, mask=(stk_amount>=cut_line))
        score = np.nanmean(active_raw, axis=1) - np.nanmean(inactive_raw, axis=1)
        factor_raw = bk.move_mean(score, 25, int(25*0.9))
        return factor_raw[-1]
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

def rolling_norm(sig, window=1200, method='max_min'):
    assert isinstance(sig, pd.Series) or isinstance(sig, pd.DataFrame) or isinstance(sig, np.ndarray), 'input must be a series, dataframe or ndarray'
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
            elif isinstance(sig, np.ndarray):
                sig_max = bk.move_max(sig, window=window, min_count=int(window / 2), axis=0)
                sig_min = bk.move_min(sig, window=window, min_count=int(window / 2), axis=0)
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
            elif isinstance(sig, np.ndarray):
                output = bk.move_rank(sig, window=d, min_count=int(d / 2), axis=0)
            return signal

class wyc_ts44_future_nr_ar(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['close', 'amount', 'volume', 'adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[0,1]'
    handle_preadj = True 

    def calculate(self, df):
        volume = df['volume_preadj'][-1470:]
        close = df['close_preadj'][-1470:]
        temp1 = volume.copy(deep = True)
        con2 = close < close.shift(1)
        temp1[con2] = -1 * volume
        
        factor = bk.move_sum(temp1, 20, 10, axis = 0)[-1450:]
        factor = bk.move_mean(factor, 20, 10, axis = 0)[-1430:]

        factor = rolling_norm(factor, 5 * 242)[-220:]

        a = df['amount'][-220:]
        ar = (2 * a.rank(axis=1, pct=True) - 1).values
        factor = factor * ar
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 20, 10, axis = 0)[-200:]
        factor = np.nanmean(factor)
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:05:16 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd



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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:03:29 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

    
class CDO_ind_CC(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close', 'open']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
#    num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        
        hclose = data['close_000905.SH'].values[-150:]
        hopen = data['open_000905.SH'].values[-150:]
        factor = np.nanmean(hclose)-np.nanmean(hopen)
        
        return factor
##########
