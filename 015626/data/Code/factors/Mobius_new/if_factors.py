# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:42:29 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:45:39 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


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
    
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:53:39 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


    

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
        
        amount = (data['amount']).iloc[-181:]
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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:52:07 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

   
    
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

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:54:53 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

    
    
class L123_nr_vt_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 6
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'turnover_rate', 'low']
    normalize_size = 720 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        tover = data['turnover_rate'].iloc[-100:]       
        turnover = (tover.rolling(60, min_periods = 15).mean()).iloc[-40:]
        
        stk_close = data['close_preadj'].iloc[-71:]
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = ts_std(stk_ret, 30).iloc[-40:]

        temp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0)
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)    
        mask = temp3*temp4
        
        hlow = data['low_preadj'].iloc[-1280:].values
        i11 = (bk.move_min(hlow, 10, min_count = 5, axis = 0)-bk.move_min(hlow, 25, min_count = 10, axis = 0))
        i12 = bk.move_min(hlow, 20, min_count = 15, axis = 0)-bk.move_min(hlow, 30, min_count = 10, axis = 0)
        i2 = (i11-i12)
        i2 = rolling_norm(i2, 242*5)[-40:]
        tempdf = np.nanmean(i2*mask, axis = 1)
        factor = np.nanmean(tempdf)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:55:29 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *




class HL123_nr_av_CC_CFG_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 6
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor', 'high','close','amount', 'low']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        hamount = data['amount'].iloc[-150:]
        df_s = hamount.rolling(120, min_periods = 15).sum()
        stk_close = data['close_preadj'].iloc[-61:]
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = ts_std(stk_ret, 30)
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0).values[-30:]
        temp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0).values[-30:]
        mask = (temp3*temp1)

        hlow = data['low_preadj'].iloc[-1330:]
        hhigh = data['high_preadj'].iloc[-1330:]

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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:56:56 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


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
##########
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_search5_long_if(FutureFactor):
    data_type = 'Future'
    days_past = 6
    data_dict = dict()
    instrument_type = 'recent'
    # data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Continuous_Data'] = {'IC':['close']}
    normalize_size = 0
    normalize_type = 'rolling_norm'
#    num_range = '(-0.5,1]'
    
    def calculate(self, data):
        future_close = data['close_cont_IC'].values[-1250:]
        factor_raw = rolling_norm(ts_max(ts_delta(future_close, 25), 25), 1200)
        return factor_raw[-1]

##########
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_1_spot_if(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close', 'volume']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        spot_close = data['close_000300.SH'].values[-138:]
        spot_volume = data['volume_000300.SH'].values[-138:]
        spot_ret = ts_pct_change(spot_close, 1)
        log_ret = log(spot_ret+1)
        ret_std = ts_std(spot_ret, 15)
        log_ret_weight = log_ret / spot_volume * ret_std
        factor_raw = ts_sum(log_ret_weight, 120)
        return factor_raw[-1]

##########
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_mean_plus_std_if(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        spot_close = data['close_000905.SH'].values[-45:]
        spot_ret = ts_pct_change(spot_close, 5)
        ret_mean = ts_mean(spot_ret, 30)
        ret_std = ts_std(spot_ret, 30)
        factor_raw = ret_mean + 2 * ret_std
        factor_mean = ts_mean(factor_raw, 10)
        return factor_mean[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:48:15 2021

@author: appadmin
"""


import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *



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
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc6_cfg_ws_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['weight', 'close', 'adjfactor']
    normalize_size = 480
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_weight = data['weight'].values[-65:]
        stk_close = data['close_preadj'].values[-65:]
        stk_ret_short = ts_pct_change(stk_close, 10)
        stk_ret_long = ts_pct_change(stk_close, 60)
        factor_init = stk_ret_long - stk_ret_short
        factor_init[factor_init<0] = 0
        factor_raw = np.nansum(factor_init * stk_weight, axis=1)
        factor_mean = ts_mean(factor_raw, 5)
        return factor_mean[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:44:07 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

class HLTM_Aug_ind_ICIF_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low', 'open']} 
    data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'volume']}
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

class wyc_ts32_icfuture_if(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 8
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close']}
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 
    
    def calculate(self, df):
        temp = df['close_cont_IC'][-1794:]
        UP = temp.copy(deep=True)
        condition = temp > temp.shift(1)
        UP[condition] = temp.rolling(20, min_periods = 10).std()
        UP[~condition] = 0
        
        UP = UP[-1774:]
        factor = ts_truncated_ema(UP, d=60, alpha= 1/10)[-1714:]
        factor = bk.move_rank(factor, 484, 242, axis = 0)[-1230:]
        factor = bk.move_mean(factor, 20, 10, axis = 0)[-1210:]
        factor = get_norm(factor)

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:57:48 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:41:54 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *
      

# 先mask再rolling
class Crossing_Turns_ICIF_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 10
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close', 'open', 'high', 'low', 'vwap']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '(-0.5, 1]'
    instrument_type='recent'
    
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
        temp1[temp1<-1000000] = np.nan
        shift_1 = shift(hvwap, 1)
        shift_1[shift_1==0] = np.nan
        a = bk.move_sum((hvwap/shift_1-1), 30, min_count = 15)
        vwtc_r = bk.move_mean(temp1*(a), 25, min_count = 5)

        factor = ts_rank(vwtc_r, 242*3)
        factor = np.nanmean(factor[-2:])
        if factor<=-0.5:
            factor = np.nan
            
        return factor
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc3_cfg_ar_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'close', 'open', 'high', 'low', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-75:]
        stk_close = data['close_preadj'].values[-75:]
        stk_high = data['high_preadj'].values[-75:]
        stk_low = data['low_preadj'].values[-75:]
        stk_open = data['open_preadj'].values[-75:]
        amount_rank_mask = section_rank_np(stk_amount, pct=True) * 2 - 1
        a = replace_zero(stk_high - stk_low)
        b = stk_close - stk_open
        b[b<0] = np.nan
        factor_init = ts_sum(b / a, 60)
        factor_raw = np.nansum(factor_init * amount_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        return factor_mean[-1]
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc12_cfg_search_vs_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['stk_volatility', 'close', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_volatility = data['stk_volatility'].values[-45:]
        stk_close = data['close_preadj'].values[-45:]
        factor_init = ts_reg_beta(stk_close, 40)
        factor_raw = np.nansum(factor_init * stk_volatility, axis=1)
        factor_mean = ts_mean(factor_raw, 5)
        return factor_mean[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:58:06 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:49:40 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

    


class hhll_ind_CC_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low', 'open']} 
    data_dict['Index_Id'] = {'000300.SH':['close', 'high', 'low', 'open']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '(-0.5, 1]'
    
    def calculate(self, data):
       
        hhigh = data['high_000300.SH'].iloc[-121:]
        hlow = data['low_000300.SH'].iloc[-121:]
        temp = np.where((hhigh>hhigh.shift(1)) & (hlow>hlow.shift(1)), 4, np.where((hhigh<hhigh.shift(1)) & (hlow<hlow.shift(1)), 0, 1))
        
        return np.abs(np.nanmean(temp[-120:]))
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc12_cfg_search_ws_if(FutureFactor):
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
        stk_weight = data['weight'].values[-85:]
        stk_close = data['close_preadj'].values[-85:]
        factor_init = ts_reg_beta(stk_close, 40)
        factor_raw = np.nansum(factor_init * stk_weight, axis=1)
        factor_mean = ts_mean(factor_raw, 45)
        return factor_mean[-1]

##########
import bottleneck as bk
from future_factor import FutureFactor


class ZHZH_CC_IF(FutureFactor):

    data_type = 'Future' 
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IF':['high']}
    normalize_size = 1200
    normalize_type = 'ts_rank' 

    
    def calculate(self, data):
        future_high = data['high_cont_IF'].values[-130:]
       
        temp = future_high >= bk.move_max(future_high, 10, 5)
        temp = bk.move_mean(temp, 120, 5)
        return temp[-1]
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc7_cfg_cr_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['stk_index_corr_hs300', 'close', 'adjfactor']
    normalize_size = 2400
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_index_corr = data['stk_index_corr_hs300'].values[-51:]
        stk_close = data['close_preadj'].values[-51:]
        stk_index_corr_rank_mask = section_rank_np(stk_index_corr, pct=True) * 2 - 1
        stk_ret = ts_pct_change(stk_close, 5)
        b = ts_mean(stk_ret, 30)
        c = ts_std(stk_ret, 30)
        factor_init = b + c
        factor_raw = np.nansum(factor_init * stk_index_corr_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        return factor_mean[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:59:02 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


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

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:39:32 2021

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
#    num_range = '(-0, 1]'
    
    def calculate(self, data):
        
        hclose = data['close_000300.SH'].values[-62:]

        factor = np.diff(bk.move_mean(hclose, 60))
        
        return factor[-1]
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc2_cfg_ws_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['weight', 'close', 'open', 'volume', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '(-0.5,1]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_weight = data['weight'].values[-51:]
        stk_close = data['close_preadj'].values[-51:]
        stk_open = data['open_preadj'].values[-51:]
        stk_volume = data['volume_preadj'].values[-51:]
        factor_init = (stk_close - ts_delay(stk_open, 30)) * stk_volume
        factor_raw = np.nansum(factor_init * stk_weight, axis=1)
        factor_mean = ts_mean(factor_raw, 20)
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

class wyc_ts7_future_vr_if(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'stk_volatility', 'adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True 
    
    def calculate(self, df):
        N = 15
        logclose = np.log(df['close_preadj'][-191:])
        s1 = multi_processing_joblib(df=logclose, func=ts_truncated_ema, n_jobs=-1, d=60, alpha= 2/N)[-131:]
        s2 = multi_processing_joblib(df=s1, func=ts_truncated_ema, n_jobs=-1, d=60, alpha= 2/N)[-71:]
        s3 = multi_processing_joblib(df=s2, func=ts_truncated_ema, n_jobs=-1, d=60, alpha= 2/N)[-11:].values
        s3[abs(s3) < 1e-8] = np.nan
        factor = s3[1:] / s3[:-1] - 1
        
        factor = np.nanmean(factor, axis = 0)

        vr = (2 * df['stk_volatility'][-1:].rank(axis=1, pct=True) - 1).values
        factor = factor * vr
        factor = np.nansum(factor)

        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:45:05 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


class ICIF4_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low', 'open']} 
    data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
#    num_range = '(-0.5, 1]'
    
    def calculate(self, data):

        hclose = data['close_000905.SH'].values[-62:]
        temp = np.nanmean(hclose[-60:]) - np.nanmean(shift(hclose, 20)[-40:])
        factor = np.abs(temp)
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 14:01:37 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


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
    
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:49:25 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

    

class VMaxVmean_CC_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['vwap']} 
    #data_dict['Index_Id'] = {'000300.SH':['close', 'high', 'low', 'open']}
    normalize_size = 480
    normalize_type = 'ts_rank'
    instrument_type='recent'
    #num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        vwap = (data['vwap_cont_IC'].values)[-61:]
        factor = np.nanmax(vwap[-60:])/np.nanmin(vwap[-60:])

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:47:27 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *



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
##########
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_search6_long_if(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['open']}
    normalize_size = 600
    normalize_type = 'rolling_norm'
#    num_range = '(-0.5,1]'
    
    def calculate(self, data):
        spot_open = data['open_000905.SH'].values[-50:]
        factor_raw = ts_median(ts_delta(spot_open, 20), 30)
        return factor_raw[-1]

##########
from operators_wsc_1_0 import *
from future_factor import FutureFactor


class wsc4_spot_kpz_if(FutureFactor):

    data_type = 'Future' 
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    
    
    def calculate(self, data):
        spot_close = data['close_000905.SH'].values[-122:]
        
        N = 20
        dpo = spot_close - ts_delay(ts_mean(spot_close, N), int(N/2+1))
        factor_raw = abs(dpo - ts_median(dpo, 60))
        factor_mean = ts_mean(factor_raw, 30)
        return factor_mean[-1]
    
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:41:33 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *
      
class CloseVoltoMean_ICIF_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 10
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close', 'open']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        
        hclose = data['close_000905.SH'].values[-50:]
        factor0 = bk.move_std(hclose, 30, min_count = 15)/bk.move_mean(hclose, 30, min_count = 15)

        factor = np.nanmean(factor0[-15:])
   
        return factor
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc14_cfg_ar_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 3
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'close', 'adjfactor']
    normalize_size = 240*12
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-510:]
        stk_close = data['close_preadj'].values[-510:]
        amount_rank_mask = section_rank_np(stk_amount, pct=True) * 2 - 1
        n = 10
        temp = ts_sum(abs(ts_delta(stk_close, 1)), n)
        vi = abs(ts_delta(stk_close, n)) / replace_zero(temp)
        vidya = vi * stk_close + (1-vi) * ts_delay(stk_close, 1)
        factor_init = rolling_norm(vidya, 480)
        factor_raw = np.nansum(factor_init * amount_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        return factor_mean[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 17:44:21 2021

@author: appadmin
"""

import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_cc import *
from operators_wsc_1_0 import *
from future_factor import FutureFactor


class Short_CFG27_CC_IF(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = ['volume', 'low', 'high', 'close']
    normalize_size = 10*240
    normalize_type = 'ts_rank' 

    handle_preadj = False
    
    def calculate(self, data):
        
        hclose = data['close'].values[-188:]
        hhigh = data['high'].values[-188:]
        hlow = data['low'].values[-188:]
        hvolume = data['volume'].values[-188:]
        
        hret = (hclose[1:]/hclose[:-1] - 1)[-36:]
        temp1 = bk.move_max(hhigh, 90, 7, axis = 0)-hclose
        temp2 = hclose-bk.move_min(hlow, 90, 7, axis = 0)
        
        temp11 = (temp1>temp2)
        temp22 = (temp2>=temp1)

        temp = temp11*temp1 + temp22*temp2
        i1 = bk.move_mean(temp*hvolume, 60, 2, axis = 0)[-36:]
        
        
        df_s_mask = np.nanmedian(i1, axis=1)
        

        df_s_mask = np.expand_dims(df_s_mask, axis=-1)

        hret_1 = ma.array(hret, mask=(i1<=df_s_mask))

        hret_2 = ma.array(hret, mask=(i1>=df_s_mask))
        
        temp2 = np.nanmean(hret_1, axis=1) - np.nanmean(hret_2, axis=1)
        factor = np.nanmean(temp2[-35:])
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:51:49 2021

@author: appadmin
"""


import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


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
   
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class xdy_ts1_spot_if(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close','high']}
    normalize_size = 5 * 242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.5,1]'
    handle_preadj = None 

    def calculate(self, df):
        high = df['high_000300.SH'][-80:].values
        close = df['close_000300.SH'][-80:].values
        high[abs(high) < 1e-8] = np.nan
        gain_high_30 = (high[30:] / high[:-30] - 1)[-20:]
        h_c = (close / high - 1)
        a = bk.move_mean(h_c, 60, 30, axis = 0)[-20:]
        a[abs(a) < 1e-8] = np.nan
        factor = bk.move_sum(gain_high_30 / a, 10, 5, axis = 0)[-10:]
        factor = np.nanmean(factor) * -1
        return factor
##########
import bottleneck as bk
from operators_cc import *
from future_factor import FutureFactor

class LminLmean_ICIF_CC_IF(FutureFactor):

    data_type = 'Future' 
    days_past = 3
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IC':['low']}
    normalize_size = 484
    normalize_type = 'rolling_norm' 
    
    
    def calculate(self, data):
        future_low = data['low_cont_IC'].values[-549:]
        
        ctl_r = -bk.move_min(future_low, 60, 15) / bk.move_mean(future_low, 15, 5)
        factor = rolling_norm(ctl_r, 484)
        factor = bk.move_mean(factor, 5, 3)
        return factor[-1]
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

class wyc_ts6_spot_if(FutureFactor):
    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 2
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Index_Id'] = {'000300.SH':['close','high','low','volume']}
    normalize_size = 1210 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, df):
        close = df['close_000300.SH'][-460:]
        high = df['high_000300.SH'][-460:]
        low = df['low_000300.SH'][-460:]
        volume = df['volume_000300.SH'][-460:]
        
        a = high- low
        b = volume * ((close - low) - (high - close))
        c = b / a
        c = c.replace([np.inf, -np.inf], np.nan)
        
        factor = ts_truncated_ema(c, 200, 1/20)[-260:].values
        factor = bk.move_rank(factor, 240, 120, axis = 0)[-20:]
        factor = np.nanmean(factor)

        return factor
##########
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_gp3_spot_if(FutureFactor):
    data_type = 'Future'
    days_past = 2
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['low']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        spot_low = data['low_000300.SH'].values[-260:]
        factor_raw = ts_median(ts_delta(ts_pct_change(spot_low, 120), 115), 25)
        return factor_raw[-1]
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_ts4_icspot_if(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 2
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']} 
    normalize_size = 5 * 242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None
    
    def calculate(self, df):

        close = df['close_000905.SH'][-400:].values
        
        csum = bk.move_sum(close, 100, 50, axis = 0) / 100
        standard = (csum[100:] - csum[:-100]) / close[:-100]
        
        c1 = -1 * (close - bk.move_min(close, 100, 50, axis = 0))
        c2 = -1 * (close[3:] - close[:-3])
        factor = np.where(standard[-200:]<=0.05, c1[-200:], c2[-200:])
        factor = bk.move_rank(-1*factor, 100, 50, axis = 0)[-100:]
        factor = np.nanmean(factor)

        return factor

##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

def ts_std(df1, d):
    # moving time-series rank for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                           index=df1.index, name=df1.name)
    return output

class wyc_ts14_icspot_if(FutureFactor):
    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1210 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
   
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, df):
        close = df['close_000905.SH'][-141:]
        factor = np.where(close > close.shift(1), ts_std(close, 50), 0)[-90:]
        factor = bk.move_rank(factor, 60, 30, axis = 0)[-30:]
        factor = np.nanmean(factor)
        return factor
##########
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_gp1_future_if(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    # data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Continuous_Data'] = {'IF':['low', 'amount', 'OpenInterest']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        future_low = data['low_cont_IF'].values[-115:]
        future_amount = data['amount_cont_IF'].values[-115:]
        future_position = data['OpenInterest_cont_IF'].values[-115:]
        factor_raw = max2(rolling_norm(future_low, 115), ts_corr(future_amount, future_position, 90))
        return factor_raw[-1]
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from future_factor import FutureFactor

class rt1_zf_if(FutureFactor):
    '''
    期货类因子
    '''
    data_type = 'Future' #'IndexStock'
    days_past = 3
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close','low']}
    normalize_size = 0 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'

    def calculate(self, data):
        close = data['close_000300.SH'].iloc[-242*2-71:].values
        low = data['low_000300.SH'].iloc[-242*2-71:].values
        lowmin = bk.move_min(low, window = 60, min_count = 30)
        sig = close/lowmin
        sig = bk.move_rank(sig, window = 242*2, min_count = 242)
        sig = np.nanmean(sig[-10:])
        if sig <=-0.5:
            return 0
        else:
            return sig


##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_ts20_icspot_if(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 5
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close','high','low','volume']}
    normalize_size = 4 * 242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 

    def calculate(self, df):
        close = df['close_000905.SH'][-1008:]
        high = df['high_000905.SH'][-1008:]
        low = df['low_000905.SH'][-1008:]
        volume = df['volume_000905.SH'][-1008:]
        
        a = high - low
        a[abs(a) < 1e-8] = np.nan
        factor = bk.move_sum(((close - low) - (high - close)) / a * volume, 20, 10, axis = 0)[-988:]
        
        factor = bk.move_rank(factor, 968, 484, axis = 0)[-20:]
        factor = np.nanmean(factor)
        
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

class wyc_ts39_icfuture_if(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close']}
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.5,1]'
    handle_preadj = None

    def calculate(self, df):
        
        close = df['close_cont_IC'][-1440:]
        close = (close - close.shift(20))[-1420:]
        
        factor = ts_truncated_ema(close, d=200, alpha= 1/30)[-1220:]

        factor = bk.move_mean(factor, 10)[-1210:]
        factor = get_norm(factor)

        return factor

##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *


class wsc5_cfg_ar_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'close', 'adjfactor']
    normalize_size = 240
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-100:]
        stk_close = data['close_preadj'].values[-100:]
        amount_rank_mask = section_rank_np(stk_amount, pct=True) * 2 - 1
        ma_long = ts_mean(stk_close, 90)
        ma_short = ts_mean(stk_close, 15)
        ma_diff = ma_short - ma_long
        factor_raw = np.nansum(ma_diff * amount_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 10)
        return factor_mean[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:43:12 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


class HL123_ICIF_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low', 'open']} 
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
#    num_range = '(-0.5, 1]'
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

class wyc_ts38_icspot_if(FutureFactor):
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
        closestd = close.rolling(10, min_periods = 5).std()
        temp1[condition] = closestd
        temp1[~condition] = 0
        a = ts_truncated_ema(temp1[-1350:], 5 * 242, 1/50).values[-140:]

        temp1[condition] = 0
        temp1[~condition] = closestd
        b = ts_truncated_ema(temp1[-1350:], 5 * 242, 1/50).values[-140:]

        c = a + b
        c[abs(c) < 1e-8] = np.nan
        factor = a / c * 100
        factor = bk.move_rank(factor, 120, 60, axis = 0)[-20:]
        factor = np.nanmean(factor)

        return factor
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class xdy_ts6_spot_if(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 5*242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None
    
    def calculate(self, df):
        close = df['close_000300.SH'][-185:].values
        gain_close_15 = close[15:]/close[:-15] - 1
        factor = 2 * gain_close_15[20:] - gain_close_15[:-20]
        factor = np.nanmean(factor)
        return factor
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd
import scipy

class xdy_ts4_spot_if(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['high']}
    normalize_size = 5 * 242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 
    
    def calculate(self, df):
        high = df['high_000300.SH'][-105:].values
        fmax = bk.move_max(high, 30, 15, axis = 0)
        fmin = bk.move_min(high, 30, 15, axis = 0)
        a = fmax - fmin
        a[a<1e-8] = np.nan
        factor = ((high - fmin) / a)[-75:]
        
        factor = -1 * scipy.stats.skew(factor, bias = False)

        return factor
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

def get_delta(data, n):
    return data[n:] - data[:-n]

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
        
        
class wyc_ts5_future_nr_tr_if(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 12
    data_dict = dict()
    data_dict['Stock'] = ['close','turnover_rate','adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[0,1]'
    handle_preadj = True

    def calculate(self, df):
        N = 45
        close = df['close_preadj'][-2830:].values
        origin = get_delta((bk.move_sum(close, N,int(N/2), axis =0) / N), N) / close[:-N]
        change1 = -1 * (close - bk.move_min(close, N,int(N/2), axis =0))[N:]
        change2 = -1 * get_delta(close, 3)[N-3:]
        factor = np.where(origin<=0.05,change1,change2)[-2740:]

        factor = bk.move_rank(-1*factor, 1200, 600, axis = 0)[-1540:]
        factor = bk.move_mean(factor, 15, 7, axis = 0)[-1525:]

        factor = rolling_norm(factor, 5 * 242)[-315:]

        t = df['turnover_rate'][-315:]
        tr = (2 * t.rank(axis=1, pct=True) - 1).values
        factor = factor * tr
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 300, 150, axis = 0)[-15:]
        factor = np.nanmean(factor)
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:46:10 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


class LMLS_ind_ICIF_CC_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['low']} 
    #data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
#    num_range = '(-0.5, 1]'
    instrument_type='recent'
    
    def calculate(self, data):
        low = data['low_cont_IC'].values[-90:]
        factor = np.nanmean(low[-75:]) - np.nanmean(shift(low, 30)[-45:])
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 17:55:14 2021

@author: appadmin
"""

import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_cc import *
from operators_wsc_1_0 import *
from future_factor import FutureFactor

class Short_CFG7_CC_IF(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['turnover_rate', 'close', 'open', 'adjfactor', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank'

    handle_preadj = True

    def calculate(self, data):
        stk_close = data['close_preadj'].values[-152:]
        stk_open = data['open_preadj'].values[-152:]
        stk_turnover = data['turnover_rate'].values[-152:]
        ww = data['weight'].values[-152:]
        ret = stk_close / stk_open - 1
        hret = ts_pct_change(stk_close, 1)*ww
        stk_turnover[stk_close >= stk_open] = np.nan
        ret[stk_close >= stk_open] = np.nan
        cc1 = stk_turnover / r(abs(ret))
        ccc1 = bk.move_mean(cc1, 120, 7, axis=0)*ww
        ccc1_mask = np.expand_dims(np.nanmedian(ccc1, axis=1), axis=-1)
        hret1 = ma.array(hret, mask=(ccc1<=ccc1_mask))
        hret2 = ma.array(hret, mask=(ccc1>=ccc1_mask))
        cc2 = np.nanmean(hret1, axis=1) - np.nanmean(hret2, axis=1)
        ccc2 = np.nanmean(cc2[-30:])
        return ccc2
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:52:24 2021

@author: appadmin
"""


import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *




class CFG8_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','open', 'volume','close', 'float_shares']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.5, 1]'# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:48:34 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


    
class SLCS_CC_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 7
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IF':['close', 'high', 'low', 'open']} 
    data_dict['Index_Id'] = {'000300.SH':['close', 'high', 'low', 'open']}
    normalize_size = 242*4
    normalize_type = 'ts_rank'
#    num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        close_spot = (data['close_000300.SH'].values)[-1290:]
        ind = list(range(len(close_spot)))
        m_vwap_ind_r = rolling_linear_reg(ind, close_spot, 60)
        factor = rolling_norm(m_vwap_ind_r, method = 'ts_rank')
        factor[factor<=-0.5] = np.nan

        return factor[-1]

##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc14_cfg_cr_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['stk_index_corr_hs300', 'close', 'adjfactor']
    normalize_size = 240*8
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_index_corr = data['stk_index_corr_hs300'].values[-117:]
        stk_close = data['close_preadj'].values[-117:]
        stk_index_corr_rank_mask = section_rank_np(stk_index_corr, pct=True) * 2 - 1
        n = 10
        temp = ts_sum(abs(ts_delta(stk_close, 1)), n)
        vi = abs(ts_delta(stk_close, n)) / replace_zero(temp)
        vidya = vi * stk_close + (1-vi) * ts_delay(stk_close, 1)
        factor_init = rolling_norm(vidya, 90)
        factor_raw = np.nansum(factor_init * stk_index_corr_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        return factor_mean[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:43:31 2021

@author: appadmin
"""
import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


class HLDL2_ind_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low', 'open']} 
    data_dict['Index_Id'] = {'000300.SH':['close', 'high', 'low', 'open']}
    normalize_size = 5 * 240
    normalize_type = 'rolling_norm'
#    num_range = '[-0, 1]'
    
    def calculate(self, data):
        hlow = (data['low_000300.SH'].values)[-120:]
        hhigh = (data['high_000300.SH'].values)[-120:]
        t_pcorr = (np.diff(hhigh)+np.diff(hlow))
        factor = np.nanmean(t_pcorr[-90:])
        return factor

##########
from future_factor import FutureFactor
from operators_wsc_1_0 import *


class wsc_mean_plus_std2_if(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        spot_close = data['close_000300.SH'].values[-45:]
        spot_ret = ts_pct_change(spot_close, 5)
        ret_mean = ts_mean(spot_ret, 30)
        ret_std = ts_std(spot_ret, 30)
        factor_raw = 1.5 * ret_mean + ret_std
        factor_mean = ts_mean(factor_raw, 10)
        return factor_mean[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:42:12 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


class GA_ind_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close', 'high', 'low', 'open']} 
    normalize_size = 3 * 242
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
        
class wyc_ts34_future_nr_as_if(FutureFactor):
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
        high = df['high_preadj'][-1525:].values
        low = df['low_preadj'][-1525:].values
        close = df['close_preadj'][-1525:].values
        volume = df['volume_preadj'][-1525:].values
        chl = high - low
        chl[abs(chl) < 1e-6] = np.nan
        factor = ((close - low)-(high - close))/ chl * volume
        factor = bk.move_mean(factor, 150, 75, axis = 0)[-1375:]

        factor = rolling_norm(factor, 5 * 242)[-165:]

        a = df['amount'][-165:].values
        factor = factor * a
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 150, 75, axis = 0)[-15:]
        factor = np.nanmean(factor)
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

class wyc_ts49_future_if(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['close']}
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 

    def calculate(self, df):
        close = df['close_cont_IF'][-1615:]
        csum = bk.move_sum(close, 100, 50, axis = 0) / 100
        con1 = ((csum[100:] - csum[:-100]) / close.shift(100)[100:]) <= 0.05
        
        temp1 = close[100:].copy(deep = True)
        temp1[con1] = close - bk.move_min(close, 200, 100, axis = 0)
        temp1[~con1] = close - close.shift(10)
        
        factor = bk.move_rank(temp1, 75, 37, axis = 0)[-1240:]
        factor = bk.move_mean(factor, 30, 15, axis = 0)[-1210:]
        factor = get_norm(factor)
   
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:59:20 2021

@author: appadmin
"""


import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

   
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


class wyc_ts6_future_ws_if(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['close', 'weight', 'high', 'low', 'volume', 'adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[-1,0]'
    handle_preadj = True 

    def calculate(self, df):
        a = df['high_preadj'][-1575:] - df['low_preadj'][-1575:]
        a[abs(a) < 1e-8] = np.nan
        factor = df['volume_preadj'][-1575:] * ((df['close_preadj'][-1575:] - df['low_preadj'][-1575:]) - (df['high_preadj'][-1575:] - df['close_preadj'][-1575:])) / a
        factor = multi_processing_joblib(df=factor, func=ts_truncated_ema, n_jobs=-1, d=200, alpha= 1/45).values[-1375:]
        factor = bk.move_rank(factor, 1200, 600, axis = 0)[-175:]
        factor = bk.move_mean(factor, 15, 7, axis = 0)[-160:]

        factor = factor * df['weight'][-160:].values
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 150, 75, axis = 0)[-10:]
        factor = np.nanmean(factor)
      
        return factor
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero, replace_inf



class wsc9_cfg_ws_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Index_Id'] = {'000300.SH':['close']}
    data_dict['Stock'] = ['weight', 'close', 'adjfactor']
    normalize_size = 480
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_weight = data['weight'].values[-189:]
        stk_close = data['close_preadj'].values[-189:]
        spot_close = data['close_000300.SH'].values[-189:]
        spot_ret = ts_pct_change(spot_close, 3)
        stk_ret = ts_pct_change(stk_close, 3)
        ret_diff = stk_ret - spot_ret
        ret_diff_bool = (ret_diff > 0) + 0.0
        ret_diff_bool[np.isnan(ret_diff)] = np.nan
        temp = ts_sum(ret_diff_bool, 120)
        factor_init = replace_inf(ts_sum(ret_diff_bool, 20) / replace_zero(temp))
        factor_raw = np.nansum(factor_init * stk_weight, axis=1)
        factor_mean = -ts_mean(factor_raw, 45)
        return factor_mean[-1]

##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_ts14_spot_if(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 5 * 242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.5,1]'
    handle_preadj = None 
    
    def calculate(self, df):
        close = df['close_000300.SH'][-150:]
        factor = np.where(close > close.shift(1), close.rolling(50, min_periods=25).std(), 0)[-100:]
        factor = ((bk.move_rank(factor, 60, 30, axis = 0) + 1) / 2)[-40:]
        factor = np.nanmean(factor)

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:53:57 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *



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
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from future_factor import FutureFactor

class sr1_zf_if(FutureFactor):
    '''
    期货类因子
    '''
    data_type = 'Future' #'IndexStock'
    days_past = 3
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close','low']}
    normalize_size = 0 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'

    def calculate(self, data):
        close = data['close_000300.SH'].iloc[-242*2-70:].values
        low = data['low_000300.SH'].iloc[-242*2-70:].values

        rtn = close[1:]/close[:-1]-1
        vol = bk.move_std(rtn, window = 60, min_count = 30)
        vol[vol<1e-8] = np.nan
        lowmin = bk.move_min(low[:-1],window = 60, min_count = 30)
        ret = close[1:]/lowmin -1       
        sig = ret/vol
        sig = bk.move_rank(sig, window = 242*2, min_count=242)
        sig = np.nanmean(sig[-5:])
        if sig <=-0.5:
            return 0
        else:
            return sig
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:51:30 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *



class CFG30_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','amount', 'close']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[0, 1]'# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:45:54 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


    
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
    
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc10_spot_kpz_if(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '(-0.5,1]'
    
    def calculate(self, data):
        spot_close = data['close_000905.SH'].values[-94:]
        spot_high = data['high_000905.SH'].values[-94:]
        spot_low = data['low_000905.SH'].values[-94:]
        n = 30
        hl = spot_high + spot_low
        high_abs = abs(ts_delta(spot_high, 1))
        low_abs = abs(ts_delta(spot_low, 1))
        dmz = np.maximum(high_abs, low_abs)
        dmz[ts_delta(hl, 1)<=0] = 0
        dmf = np.maximum(high_abs, low_abs)
        dmf[ts_delta(hl, 1)>=0] = 0
        a = ts_sum(dmz, n) + ts_sum(dmf, n)
        ddi = (ts_sum(dmz, n) - ts_sum(dmf, n)) / replace_zero(a)
        factor_raw = ts_mean(ddi, 60)
        return factor_raw[-1]

##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *


class wsc8_cfg_as_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'close', 'volume', 'adjfactor']
    normalize_size = 720
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-70:]
        stk_close = data['close_preadj'].values[-70:]
        stk_volume = data['volume_preadj'].values[-70:]
        factor_init = ts_cov(stk_close, stk_volume, 55)
        factor_raw = np.nansum(factor_init * stk_amount, axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        return factor_mean[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:47:58 2021

@author: appadmin
"""


import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *



class RolTrendLS_CC_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['close', 'high', 'low', 'open']} 
    #data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    instrument_type='recent'
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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:49:08 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

    
        
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
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc7_cfg_ar_if(FutureFactor):
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
        stk_amount = data['amount'].values[-71:]
        stk_close = data['close_preadj'].values[-71:]
        amount_rank_mask = section_rank_np(stk_amount, pct=True) * 2 - 1
        stk_ret = ts_pct_change(stk_close, 5)
        b = ts_mean(stk_ret, 30)
        c = ts_std(stk_ret, 30)
        factor_init = 3 * b + c
        factor_raw = np.nansum(factor_init * amount_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 35)
        return factor_mean[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:56:02 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

    
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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:52:41 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

    
class ClMaxClMin_nr_wt_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close','turnover_rate', 'weight']
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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:50:29 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


    
    
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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:54:37 2021

@author: appadmin
"""


import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

    

class L123_nr_ac_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 6
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
        
        hlow = data['low_preadj'].iloc[-1285:].values
        i11 = (bk.move_min(hlow, 10, min_count = 5, axis = 0)-bk.move_min(hlow, 25, min_count = 10, axis = 0))
        i12 = bk.move_min(hlow, 20, min_count = 15, axis = 0)-bk.move_min(hlow, 30, min_count = 10, axis = 0)
        i2 = (i11-i12)
        i2 = rolling_norm(i2, 242*5)[-45:]
        tempdf = np.nanmean(i2*mask, axis = 1)
        factor = np.nanmean(tempdf)
        
        return factor
    
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc21_cfg_ar_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'close', 'high', 'low', 'open', 'adjfactor']
    normalize_size = 1440
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-112:]
        stk_close = data['close_preadj'].values[-112:]
        stk_open = data['open_preadj'].values[-112:]
        stk_low = data['low_preadj'].values[-112:]
        stk_high = data['high_preadj'].values[-112:]
        amount_rank_mask = section_rank_np(stk_amount, pct=True) * 2 - 1
        n = 45
        a = abs(stk_high-ts_delay(stk_close, 1))
        b = abs(stk_low-ts_delay(stk_close, 1))
        c = abs(stk_high-ts_delay(stk_low, 1))
        d = abs(ts_delay(stk_close, 1)-ts_delay(stk_open, 1))
        k = np.maximum(a, b)
        m = ts_max(stk_high-stk_low, n)
        r1 = a + 0.5*b + 0.25*d
        r2 = b + 0.5*a + 0.25*d
        r3 = c + 0.25*d
        r4 = np.where((a>=b)&(a>=c), r1, r2)
        r = np.where((c>=a)&(c>=b), r3, r4)
        si = 50 * (ts_delta(stk_close, 1) + ts_delay(stk_close, 1) - ts_delay(stk_open, 1) + 0.5*(stk_close - stk_open))\
                / replace_zero(r) * k / replace_zero(m)
        factor_raw = np.nansum(si * amount_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 65)
        return factor_mean[-1]
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:45:22 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


class L123_ICIF_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low', 'open']} 
    #data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
#    num_range = '(-0.5, 1]'
    instrument_type='recent'
    
    def calculate(self, data):

        hlow = (data['low_cont_IC'].values)[-90:]
        i11 = bk.move_min(hlow, 10, min_count = 5) - bk.move_min(hlow, 25, min_count = 10)
        i12 = bk.move_min(hlow, 20, min_count = 15) - bk.move_min(hlow, 30, min_count = 10)
        i2 = np.nanmean((i11 -i12)[-30:])

        return i2
    
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:46:52 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


class LminC_ind_CC_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IC':['vwap']} 
    data_dict['Index_Id'] = {'000300.SH':['close', 'low']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '[-0.8, 1]'
    
    def calculate(self, data):
        
        low = data['low_000300.SH'].values[-180:]
        
        return -np.nanmin(low)/(data['close_000300.SH'].values[-1])

##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero


    
class wsc_hf18_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['Buy1NumOrdersMean', 'Bid1AmtMean', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        stk_Buy1NumOrdersMean = data['Buy1NumOrdersMean'].values[-20:]
        stk_Bid1AmtMean = data['Bid1AmtMean'].values[-20:]
        stk_weight = data['weight'].values[-20:]
        factor_raw = np.nansum(stk_Bid1AmtMean / replace_zero(stk_Buy1NumOrdersMean) * stk_weight, axis=1)
        factor_mean = ts_mean(factor_raw, 20)
        return factor_mean[-1]
##########
import numpy as np
import numpy.ma as ma
from future_factor import FutureFactor
from operators_wsc_1_0 import *




class wsc_cfg7_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'amount', 'adjfactor', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '(-0.5,1]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-24:]
        stk_weight = data['weight'].values[-24:]
        stk_amount = data['amount'].values[-24:]
        stk_ret = ts_pct_change(stk_close, 3)
        stk_ret_mask = np.nanquantile(stk_ret, 0.8, axis=1, keepdims=True)
        amount_after_mask = ma.array(stk_amount, mask=(stk_ret<=stk_ret_mask))
        factor_raw = np.nansum(amount_after_mask*stk_weight, axis=1)
        factor_mean = ts_mean(factor_raw, 20)
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

class wyc_if_2hour_return_nr_ts_if(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['close','turnover_rate','adjfactor']
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, df):
        cif = df['close_preadj'].values[-1531:]
        cif[abs(cif) < 1e-8] = np.nan
        ifreturn = cif[1:] / cif[:-1] - 1
        factor = bk.move_mean(ifreturn, 200, min_count=100, axis = 0)[-1330:]

        factor = rolling_norm(factor, 5 * 242)[-120:]

        t = df['turnover_rate'][-120:].values
        factor = factor * t
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 100, 50, axis = 0)[-20:]
        factor = np.nanmean(factor)
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:58:25 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *



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
##########
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_inf



class wsc_ti5_if(FutureFactor):
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
        future_close = data['close_cont_IF'].values[-1321:]
        close_mean = ts_mean(future_close, 40)
        close_std = ts_std(future_close, 40)
        factor_raw = replace_inf(ts_pct_change(close_mean + 2 * close_std, 40))
        factor_mean = ts_rank(factor_raw, 1200)
        return factor_mean[-1]
##########
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_search3_if(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['high']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        spot_high = data['high_000905.SH'].values[-75:]
        factor_raw = ts_std(spot_high, 75)
        return factor_raw[-1]

##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc3_cfg_cr_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['stk_index_corr_hs300', 'close', 'open', 'high', 'low', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '(-0.5,1]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_index_corr = data['stk_index_corr_hs300'].values[-80:]
        stk_close = data['close_preadj'].values[-80:]
        stk_high = data['high_preadj'].values[-80:]
        stk_low = data['low_preadj'].values[-80:]
        stk_open = data['open_preadj'].values[-80:]
        stk_index_corr_rank_mask = section_rank_np(stk_index_corr, pct=True) * 2 - 1
        a = replace_zero(stk_high - stk_low)
        b = stk_close - stk_open
        b[b<0] = np.nan
        factor_init = ts_sum(b / a, 60)
        factor_raw = np.nansum(factor_init * stk_index_corr_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 20)
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

class wyc_icif_if(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close'],'IF':['close']} 
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[0,1]'
    handle_preadj = None 
 
    def calculate(self, df):
        factor = (df['close_cont_IC'] - df['close_cont_IF'])[-1290:].values
        factor = factor - bk.move_mean(factor, 60, min_count = 30, axis = 0)
        factor = bk.move_mean(factor, 20, min_count = 10, axis = 0)
        factor = get_norm(factor[-5*242:])
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

class wyc_ts19_icfuture_if(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close','high','low','volume']}
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 
    
    def calculate(self,df):
        close = df['close_cont_IC'][-1250:]
        high = df['high_cont_IC'][-1250:]
        low = df['low_cont_IC'][-1250:]
        volume = df['volume_cont_IC'][-1250:]
        
        a = high - low
        a[abs(a) < 1e-8] = np.nan
        factor = bk.move_sum(((close - low) - (high - close)) / a * volume, 20, 10, axis = 0)[-1230:]
        factor = bk.move_mean(factor, 30, 15, axis = 0)[-1200:]
        factor = get_norm(factor)
        return factor
    

##########
import bottleneck as bk
from future_factor import FutureFactor


class LminLmean_CC_IF(FutureFactor):

    data_type = 'Future' 
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IF':['low']}
    normalize_size = 484
    normalize_type = 'rolling_norm' 

    
    def calculate(self, data):
        future_low = data['low_cont_IF'].values[-90:]
        
        ctl_r = -bk.move_min(future_low, 90, 15) / bk.move_mean(future_low, 15, 5)
        return ctl_r[-1]
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 15:38:27 2021

@author: appadmin
"""


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

class Short_BS_Main_CFG6_CC_IF(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = ['WeightBuyOrderQtySumMean', 'WeightSellOrderQtySumMean',  'close', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 

    handle_preadj = False
    
    def calculate(self, data):
        
        a = (data['WeightBuyOrderQtySumMean'].iloc[-140:].values/r(data['WeightSellOrderQtySumMean'][-140:]).values)*data['weight'].iloc[-140:].values
        
        stk_close = data['close'].values[-270:]
        hret = stk_close[1:]/stk_close[:-1] - 1
        hret[abs(hret)>10000] = np.nan
        hret = ts_truncated_ema_span_1(hret, 120, 4)[-140:]
        df_s_mask = np.nanmedian(a, axis=1)
        
        df_s_mask = np.expand_dims(df_s_mask, axis=-1)

        hret_1 = ma.array(hret, mask=(a<=df_s_mask))

        hret_2 = ma.array(hret, mask=(a>=df_s_mask))
        
        temp2 = np.nanmean(hret_1, axis=1) - np.nanmean(hret_2, axis=1)
        factor = ts_truncated_ema_span_1(temp2, 120, 15)[-1]
       
        return factor
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk

class wyc_icifih_mul_if(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close'],'000300.SH':['close'],'000016.SH':['close']} 
    normalize_size = 5 * 242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[0,1]'
    handle_preadj = None 
    
    def calculate(self, df):
        factor = (df['close_000905.SH'] - 2 * df['close_000016.SH'] + df['close_000300.SH']).values[-200:]
        factor = factor[-1] - np.nanmean(factor)
        return factor


##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_ts44_spot_if(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close','volume']}
    normalize_size = 5 * 242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None

    def calculate(self, df):
        temp1 = df['volume_000300.SH'][-65:]
        close = df['close_000300.SH'][-65:]
        con2 = close < close.shift(1)
        temp1[con2] = -1 * temp1
        factor = bk.move_sum(temp1, 25, 12, axis = 0)[-40:]
        factor = np.nanmean(factor)
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:56:39 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

      
class LminC_nr_rl_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'turnover_rate', 'low']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(0, 1]'# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
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
##########
import numpy as np
from future_factor import FutureFactor
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
        
def ts_std(df1, d):
    # moving time-series rank for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                           index=df1.index, name=df1.name)
    return output

def ts_mean(data, d):
    # moving time-series mean for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if d == 1:
        output = data
    else:
        if isinstance(data, np.ndarray):
            output = bk.move_mean(data, window=d, min_count=int(d / 2), axis=0)
        if isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_mean(data, window=d, min_count=int(d / 2), axis=0),
                                  index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_mean(data, window=d, min_count=int(d / 2), axis=0),
                               index=data.index, name=data.name)
    return output

class HHLS_nr_vt_CC_CFG_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 6
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close', 'high', 'adjfactor','turnover_rate']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        stk_close = data['close_preadj'][-41:]
        stk_ret = stk_close.pct_change(1, fill_method=None)[-40:]
        stk_volatility = ts_std(stk_ret, 30)[-10:]
        turnover = ts_mean(data['turnover_rate'][-70:],60)[-10:]
        temp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0)
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)
        mask = temp3*temp4
        temp = bk.move_max(data['high_preadj'][-1310:].values,50,15,axis =0) - bk.move_max(data['high_preadj'][-1310:].shift(50).values,50,7,axis = 0)
        temp = rolling_norm(temp[-1210:], 1200)[-10:]
        tempdf = (temp*mask).values
        tempdf = np.nansum(tempdf, axis = 1)
        factor = np.nanmean(tempdf)
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:40:48 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

    
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

class wyc_ts29_icfuture_if(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close','volume']}
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.5,1]'
    handle_preadj = None 

    def calculate(self, df):
        close = df['close_cont_IC'][-1550:].values
        volume = df['volume_cont_IC'][-1530:].values
        
        factor = (close[20:] - close[:-20]) / close[:-20] * volume
        factor = bk.move_rank(factor, 300, 150, axis = 0)[-1230:]
        factor = bk.move_mean(factor, 20, 10, axis = 0)[-1210:]
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
        
        
class xdy_ts2_spot_nr_tr_if(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 8
    data_dict = dict()
    data_dict['Stock'] = ['high','low','turnover_rate','adjfactor']
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[0,1]'
    handle_preadj = True
    
    def calculate(self, df):
        high = df['high_preadj'][-1740:]
        low = df['low_preadj'][-1740:]
        high[abs(high) < 1e-8] = np.nan
        gain_high_20 = high / high.shift(20) - 1
        factor = low * gain_high_20
        factor = multi_processing_joblib(df=factor, func=ts_truncated_ema, n_jobs=-1, d=200, alpha= 1/26).values[-1520:]

        factor = rolling_norm(factor, 5 * 242)[-310:]

        t = df['turnover_rate'][-310:]
        tr = (2 * t.rank(axis=1, pct=True) - 1).values
        factor = factor * tr
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 300)[-10:]
        factor = np.nanmean(factor)
    
        return factor
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from future_factor import FutureFactor

class tr1_zf_if(FutureFactor):
    '''
    期货类因子
    '''
    data_type = 'Future' #'IndexStock'
    days_past = 2
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close','high','low']}
    normalize_size = 242*3 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.5, 1]'

    def calculate(self, data):
        close = data['close_000300.SH'].iloc[-1]
        high = data['high_000300.SH'].iloc[-121*2-1:].values
        low = data['low_000300.SH'].iloc[-121*2-1:].values
        hh = np.nanmax(high[-121*2:])
        ll = np.nanmin(low[-121*2:])
        hhll = hh+ll
        if abs(hhll) < 1e-8:
            hhll = np.nan
        return 2*close/hhll
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd


class wyc_ts19_icspot_if(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 2
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close','high','low','volume']}
    normalize_size = 5 * 242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 
    
    def calculate(self, df):
        close = df['close_000905.SH'][-372:]
        high = df['high_000905.SH'][-372:]
        low = df['low_000905.SH'][-372:]
        volume = df['volume_000905.SH'][-372:]
        
        a = high - low
        a[abs(a) < 1e-8] = np.nan
        factor = bk.move_sum(((close - low) - (high - close)) / a * volume, 10, 5, axis = 0)[-362:]
        
        factor = bk.move_rank(factor, 242, 121, axis = 0)[-120:]
        factor = np.nanmean(factor)

        return factor
    
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from future_factor import FutureFactor

class mm1_zf_if(FutureFactor):
    '''
    期货类因子
    '''
    data_type = 'Future' #'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 0 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'

    def calculate(self, data):
        close = data['close_000300.SH'].iloc[-85:].values
        close_max = bk.move_max(close,window = 60, min_count = 30)
        close_min = bk.move_min(close, window = 60, min_count = 30)
        tmp = close_max - close_min
        tmp[abs(tmp)<1e-8] = np.nan
        close_norm = (close-close_min)/tmp*2-1
        return np.nanmean(close_norm[-20:])
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc1_cfg_ws_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Index_Id'] = {'000300.SH':['close']}
    data_dict['Stock'] = ['weight', 'close', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_weight = data['weight'].values[-71:]
        stk_close = data['close_preadj'].values[-71:]
        spot_close = data['close_000300.SH'].values[-71:]
        stk_ret = ts_pct_change(stk_close, 60)
        spot_ret = ts_pct_change(spot_close, 60)
        excess_ret = stk_ret - spot_ret
        stk_weight[np.isnan(excess_ret)] = np.nan
        stk_weight[excess_ret >= 0] = np.nan
        factor_raw = np.nansum(stk_weight, axis=1)
        factor_mean = ts_mean(factor_raw, 10)
        return factor_mean[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:44:27 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

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
    

##########
import numpy as np
from future_factor import FutureFactor
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

class wyc_ts47_future_if(FutureFactor):
    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 6
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IF':['close']}    
    normalize_size = 0 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
   
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, df):
        close = df['close_cont_IF'][-1285:]
        con1 = close > close.shift(4)
        factor = bk.move_sum(con1, 50, 25, axis = 0)[-1231:]
        factor = bk.move_mean(factor, 20, 10, axis = 0)[-1211:]
        factor = rolling_norm(factor, 1210)[-1]
        return factor
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc11_cfg_vs_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['stk_volatility', 'close', 'high', 'low', 'adjfactor']
    normalize_size = 480
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_volatility = data['stk_volatility'].values[-220:]
        stk_close = data['close_preadj'].values[-220:]
        stk_high = data['high_preadj'].values[-220:]
        stk_low = data['low_preadj'].values[-220:]
        n = 30
        m = 150
        low_n = ts_min(stk_low, n)
        high_n = ts_max(stk_high, n)
        a = high_n - low_n
        stochastics = (stk_close- low_n) / replace_zero(a)
        stochastics_low = ts_min(stochastics, m)
        stochastics_high = ts_max(stochastics, m)
        c = stochastics_high - stochastics_low
        stochastics_double = (stochastics - stochastics_low) / replace_zero(c)
        factor_raw = np.nansum(stochastics_double * stk_volatility, axis=1)
        factor_mean = ts_mean(factor_raw, 40)
        return factor_mean[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:58:44 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:53:17 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


    

class GA_ind_nr_tr_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 8
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','open', 'high','close','turnover_rate', 'low']
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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:56:20 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


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
##########
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

def ts_std(df1, d):
    # moving time-series rank for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                           index=df1.index, name=df1.name)
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

class wyc_ts38_spot_if(FutureFactor):
    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 3
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Index_Id'] = {'000300.SH':['close']}    
    normalize_size = 1210 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
   
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, df):
        close = df['close_000300.SH'][-636:]
        temp1 = close.copy()
        temp1[close > close.shift(1)] = ts_std(close, 10)
        temp1[close <= close.shift(1)] = 0
        a = ts_truncated_ema(temp1, 500, 1/50)
        temp1[close > close.shift(1)] = 0
        temp1[close <= close.shift(1)] = ts_std(close, 10)
        b = ts_truncated_ema(temp1, 500, 1/50)
        c = a / (a + b) * 100
        c = c.replace([np.inf, -np.inf], np.nan)
        
        factor = c[-125:].values
        factor = bk.move_rank(factor, 120, 60, axis = 0)[-5:]
        factor = np.nanmean(factor)
        return factor
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from future_factor import FutureFactor

class ss1_zf_if(FutureFactor):
    '''
    期货类因子
    '''
    data_type = 'Future' #'IndexStock'
    days_past = 7
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close','high']}
    normalize_size = 242*5 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[-0.5, 1]'

    def calculate(self, data):
        close = data['close_000300.SH'].iloc[-250*6-10:].values
        high = data['high_000300.SH'].iloc[-250*6-10:].values

        rtn = close[5:]/close[:-5]-1
        vol = bk.move_std(rtn, window = 250, min_count = 30)
        vol[vol<1e-8] = np.nan
        highmax = bk.move_max(high[:-5],window = 250, min_count = 30)
        ret = close[5:]/highmax -1       
        sig = ret/vol
        sig = bk.move_rank(sig, window = 242*5, min_count=242)
        return sig[-1]
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 17:00:00 2021

@author: appadmin
"""

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

class Short_CDZJ_CC_IF(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = ['amount', 'BuyTradeNum', 'weight', 'close']
    normalize_size = 10*240
    normalize_type = 'ts_rank' 

    handle_preadj = False
    
    def calculate(self, data):
        
        cl = data['close'].values[-125:]
        ret = cl[1:] - cl[:-1]
        temp_rsi2 = (ret<0)
        temp_rsi1 = (ret>0)
        amount = data['amount'].values[-124:]
        btn = data['BuyTradeNum'].values[-124:]
        a = 120
        b = 35
     
        temp2 = bk.move_sum(amount, a, 5, axis = 0)[-2:]/r(bk.move_sum(btn, a, 5, axis = 0))[-2:]
        temp1 = bk.move_sum(temp_rsi2*amount, a, 5, axis = 0)[-2:]/r(bk.move_sum(temp_rsi2*btn, a, 5, axis = 0))[-2:]
        
        temp11 = bk.move_sum(temp_rsi1*amount, a, 5, axis = 0)[-2:]/r(bk.move_sum(temp_rsi1*btn, a, 5, axis = 0))[-2:]
        
        temp = ((temp1 - temp11)/r(temp2))
        
        hret = cl[1:] / cl[:-1] - 1
        hret[abs(hret)>10000] = np.nan
        hret = ts_truncated_ema_span_1(hret, 120, b)[-2:]*(data['weight'].values[-2:])
        
        df_s_mask = np.nanmedian(temp, axis=1)
        
        df_s_mask = np.expand_dims(df_s_mask, axis=-1)

        hret_1 = ma.array(hret, mask=(temp<=df_s_mask))

        hret_2 = ma.array(hret, mask=(temp>=df_s_mask))
        
        temp2 = np.nanmean(hret_1, axis=1) - np.nanmean(hret_2, axis=1)
        
        return -temp2[-1]
##########
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_search1_long_if(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1000
    normalize_type = 'rolling_norm'
#    num_range = '(-0.5,1]'
    
    def calculate(self, data):
        spot_close = data['close_000905.SH'].values[-40:]
        factor_raw = ts_reg_beta(spot_close, 40)
        return factor_raw[-1]


##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:59:59 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


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
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 17 13:27:19 2021

@author: appadmin
"""


import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class Short_BS9_2_CC_IF(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_superorder_count', 'buy_bigorder_count', 'buy_midorder_count',  'buy_smallorder_count']
    normalize_size = 1200
    normalize_type = 'ts_rank' 

    handle_preadj = False
    
    def calculate(self, data):
        
        a = data['buy_superorder_count'][-3:].fillna(0) + data['buy_bigorder_count'][-3:].fillna(0) + data['buy_midorder_count'][-3:].fillna(0) + data['buy_smallorder_count'][-3:].fillna(0)
        temp2 = (data['buy_bigorder_count'][-3:].fillna(0) + data['buy_superorder_count'][-3:].fillna(0))/ a.replace(0, np.nan)
        temp2 = temp2.replace([-np.inf, np.inf], np.nan)
        factor = np.nanmean(temp2.values,axis = 1)
        factor = np.nanmean(factor)
        
        return factor
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc1_cfg_ar_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Index_Id'] = {'000300.SH':['close']}
    data_dict['Stock'] = ['amount', 'close', 'adjfactor']
    normalize_size = 600
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-76:]
        stk_close = data['close_preadj'].values[-76:]
        spot_close = data['close_000300.SH'].values[-76:]
        amount_rank_mask = section_rank_np(stk_amount, pct=True) * 2 - 1
        stk_ret = ts_pct_change(stk_close, 60)
        spot_ret = ts_pct_change(spot_close, 60)
        excess_ret = stk_ret - spot_ret
        amount_rank_mask[np.isnan(excess_ret)] = np.nan
        amount_rank_mask[excess_ret >= 0] = np.nan
        factor_raw = -np.nanmean(amount_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        return factor_mean[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:50:10 2021

@author: appadmin
"""


import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *



class BS_Main2_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['SellUniqueOrderNum', 'BuyUniqueOrderNum', 'close', 'amount']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[0, 1]' # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
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
    data_argsort = bk.rankdata(data, axis=1)
    data_argsort[np.isnan(data)] = np.nan  # numpy argsort会让nan也参与排序，但是pandas不会，所以把这些值重新置为nan
    if pct == True:
        data_argsort = data_argsort / (~np.isnan(data)).sum(axis=1, keepdims=True)
    return data_argsort


class wsc13_cfg_vr_if(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'low', 'high', 'open', 'stk_volatility', 'adjfactor']
    normalize_size = 480
    normalize_type = 'ts_rank' 
    
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-47:]
        stk_low = data['low_preadj'].values[-47:]
        stk_open = data['open_preadj'].values[-47:]
        stk_high = data['high_preadj'].values[-47:]
        stk_volatility_hs300 = data['stk_volatility'].values[-47:]
        
        vol_rank = section_rank_bk(stk_volatility_hs300, pct=True) * 2 - 1
        stk_price = (stk_close + stk_low + stk_high + stk_open) / 4
        n = 45
        rpp = ts_sum(stk_price, n)
        high_n = ts_max(stk_high, n)
        low_n = ts_min(stk_low, n)
        arpp = (rpp - low_n) / replace_zero(high_n - low_n)
        factor_raw = np.nansum(arpp * vol_rank, axis=1)
        factor_mean = ts_mean(factor_raw, 2)
        return factor_mean[-1]
    


##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class xdy_ts1_spot_tr_if(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = ['close', 'high', 'turnover_rate', 'adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, df):
        high = df['high_preadj'][-385:].values
        close = df['close_preadj'][-385:].values
        high[abs(high) < 1e-8] = np.nan
        gain_high_60 = (high[60:] / high[:-60] - 1)[-325:]
        h_c = close / high - 1
        a = bk.move_mean(h_c, 60, 30, axis = 0)[-325:]
        a[abs(a) < 1e-8] = np.nan
        factor = bk.move_sum(gain_high_60 / a, 10, 5, axis = 0)[-315:]
        factor = -1 * bk.move_mean(factor, 10, 5, axis = 0)[-305:]

        tr = (2 * df['turnover_rate'][-305:].rank(axis=1, pct=True) - 1).values
        factor = factor * tr
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 300, 150, axis = 0)[-5:]
        factor = np.nanmean(factor)
        
        return factor
    
##########
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_wsc_1_0 import *
from future_factor import FutureFactor


class LminLmean_nr_cv_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 6
    data_dict = dict()
    data_dict['Stock'] = ['close', 'low', 'stk_index_corr_hs300', 'adjfactor']
    normalize_size = 720
    normalize_type = 'ts_rank' 
    
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-1275:]
        stk_low = data['low_preadj'].values[-1275:]
        stk_index_corr_hs300 = data['stk_index_corr_hs300'].values[-1275:]

        stk_ret = ts_pct_change(stk_close, 1)
        stk_vol = ts_std(stk_ret, 30)
        mask1 = np.nanquantile(stk_index_corr_hs300, 0.8, axis=1)
        mask1 = np.expand_dims(mask1, axis=-1)
        mask2 = np.nanquantile(stk_vol, 0.8, axis=1)
        mask2 = np.expand_dims(mask2, axis=-1)
        ctl_r = -bk.move_min(stk_low, 60, 15, axis=0) / bk.move_mean(stk_low, 30, 10, axis=0)
        ctl_r = rolling_norm(ctl_r, 242*5)
        tempdf = ma.array(ctl_r, mask=((stk_index_corr_hs300<=mask1)|(stk_vol<=mask2)))
        tempdf = np.nansum(tempdf, axis=1)
        factor = bk.move_mean(tempdf, 5, 2)
        return factor[-1]
##########
import numpy as np
import numpy.ma as ma
from future_factor import FutureFactor
from operators_wsc_1_0 import *

class wsc20_cfg_ar_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'close', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'rolling_norm'
#    num_range = '(0,1]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-87:]
        stk_close = data['close_preadj'][-87:]
        stk_ret = ts_pct_change(stk_close.values, 1)
        stk_skew = stk_close.rolling(30, min_periods = 15).skew().values
        stk_skew_mask = np.nanquantile(stk_skew, 0.5, axis=1, keepdims=True)
        factor_init = ma.array(stk_ret, mask=(stk_skew<=stk_skew_mask))
        factor_raw = np.nansum(factor_init * stk_amount, axis=1) / np.nansum(stk_amount * (stk_skew>stk_skew_mask), axis=1)
        factor_mean = ts_mean(factor_raw, 55)
        return factor_mean[-1]
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc22_cfg_search_as_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'open', 'adjfactor']
    normalize_size = 2400
    normalize_type = 'ts_rank'
#    num_range = '(0,1]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-56:]
        stk_open = data['open_preadj'].values[-56:]
        factor_init = ts_median(ts_delta(stk_open, 25), 25)
        factor_raw = np.nansum(factor_init * stk_amount, axis=1)
        factor_mean = ts_mean(factor_raw, 5)
        return factor_mean[-1]

##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

def get_delta(data, n):
    return data[n:] - data[:-n]

def get_norm(fa):
    fmax = np.nanmax(fa)
    fmin = np.nanmin(fa)
    divisor = fmax - fmin
    if divisor < 1e-8:
        divisior = np.nan
    return ((fa[-1] - fmin)/ divisor) * 2 - 1

class wyc_ts5_icfuture_if(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 11
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close']} 
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.8,1]'
    handle_preadj = None

    def calculate(self, df):
        N = 45
        close = df['close_cont_IC'][-2515:].values
        origin = get_delta((bk.move_sum(close, N,int(N/2), axis =0) / N), N) / close[:-N]
        change1 = -1 * (close - bk.move_min(close, N,int(N/2), axis =0))[N:]
        change2 = -1 * get_delta(close, 3)[N-3:]
        factor = np.where(origin<=0.05,change1,change2)[-2425:]

        factor = bk.move_rank(-1*factor, 1200, 600, axis = 0)[-1225:]
        factor = bk.move_mean(factor, 15, 7, axis = 0)[-1210:]
        
        factor = get_norm(factor)
        
        return factor
##########
from future_factor import FutureFactor
from operators_wsc_1_0 import *


class wsc3_future_if(FutureFactor):
    data_type = 'Future'
    days_past = 6
    data_dict = dict()
    instrument_type = 'recent'
    # data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Continuous_Data'] = {'IF':['close']}
    normalize_size = 1
    normalize_type = 'ts_rank'
#    num_range = '(-0.5,1]'
    
    def calculate(self, data):
        future_close = data['close_cont_IF'].values[-1240:]
        future_ret = ts_pct_change(future_close, 5)
        ret_mean = ts_mean(future_ret, 24)
        ret_std = ts_std(future_ret, 24)
        factor_init = ret_mean + 2 * ret_std
        factor_raw = ts_mean(factor_init, 10)
        factor_mean = ts_rank(factor_raw, 1200)
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

def delay(A,n):
    #A_(i-n)
    #A为df类型
    return A.shift(periods=n)

def ts_mean(A, d):
    # moving time-series average for the past d periods
    if isinstance(A, pd.Series):
        A = A.to_frame()
    output = pd.DataFrame(bk.move_mean(A, window=d, min_count=d//2, axis=0),
                          index=A.index, columns=A.columns)
    return output

class wyc_ts26_future_if(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 18
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['close']}
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 

    def calculate(self, df):
        N = 6
        N1 = 4
        N2 = 8
        close = df['close_cont_IF'][-4223:]
        MTM = close - close.shift(1)
        MTMMA = ts_truncated_ema(MTM, 1200, 1/6)[-3022:]
        DIF = (ts_mean(delay(MTMMA, 1), 4) - ts_mean(delay(MTMMA, 1), 8))[-3014:]
        factor = ts_truncated_ema(DIF, 1200, 1/90)[-1814:]
        factor = bk.move_rank(factor, 484, 242, axis = 0)[-1330:]
        factor = bk.move_mean(factor, 120, 60, axis = 0)[-1210:]
        factor = get_norm(factor)
        
        return factor

##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class xdy_ts1_spot_cr_if(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'high', 'stk_index_corr_hs300', 'adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[-1,0]'
    handle_preadj = True

    def calculate(self, df):
        high = df['high_preadj'][-235:].values
        close = df['close_preadj'][-235:].values
        high[abs(high) < 1e-8] = np.nan
        gain_high_60 = (high[60:] / high[:-60] - 1)[-175:]
        h_c = close / high - 1
        a = bk.move_mean(h_c, 60, 30, axis = 0)[-175:]
        a[abs(a) < 1e-8] = np.nan
        factor = bk.move_sum(gain_high_60 / a, 10, 5, axis = 0)[-165:]
        factor = -1 * bk.move_mean(factor, 10, 5, axis = 0)[-155:]

        cr = (2 * df['stk_index_corr_hs300'][-155:].rank(axis=1, pct=True) - 1).values
        factor = factor * cr
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 150, 75, axis = 0)[-5:]
        factor = np.nanmean(factor)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:53:01 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

   

class Crossing_Turns_tr_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','open', 'amount','volume','close','turnover_rate', 'high', 'low']
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
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

def get_delta(data, n):
    return data[n:] - data[:-n]

class wyc_ts5_future_cr_if(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Stock'] = ['close','stk_index_corr_hs300','adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[0,1]'
    handle_preadj = True
    
    def calculate(self, df):

        N = 45
        close = df['close_preadj'][-1305:].values
        origin = get_delta((bk.move_sum(close, N,int(N/2), axis =0) / N), N) / close[:-N]
        change1 = -1 * (close - bk.move_min(close, N,int(N/2), axis =0))[N:]
        change2 = -1 * get_delta(close, 3)[N-3:]
        factor = np.where(origin<=0.05,change1,change2)[-1215:]

        factor = bk.move_rank(-1*factor, 1200, 600, axis = 0)[-15:]
        factor = np.nanmean(factor, axis = 0)

        cr = (2 * df['stk_index_corr_hs300'][-1:].rank(axis=1, pct=True) - 1)
        factor = factor * cr
        factor = np.nansum(factor, axis=1)
        
        return factor

##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc3_cfg_as_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'close', 'open', 'high', 'low', 'adjfactor']
    normalize_size = 1800
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-85:]
        stk_close = data['close_preadj'].values[-85:]
        stk_high = data['high_preadj'].values[-85:]
        stk_low = data['low_preadj'].values[-85:]
        stk_open = data['open_preadj'].values[-85:]
        a = replace_zero(stk_high - stk_low)
        b = stk_close - stk_open
        b[b<0] = np.nan
        factor_init = ts_sum(b / a, 60)
        factor_raw = np.nansum(factor_init * stk_amount, axis=1)
        factor_mean = ts_mean(factor_raw, 25)
        return factor_mean[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:55:12 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


    

class L123_nr_wv_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 6
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','close', 'weight', 'low']
    normalize_size = 2400 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        stk_weight = (data['weight']).iloc[-60:].values
        
        stk_close = data['close_preadj'].iloc[-91:]
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = ts_std(stk_ret, 30).iloc[-60:]
        
        temp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0)
        mask = stk_weight*temp3
        
        hlow = data['low_preadj'].iloc[-1290:].values
        i11 = (bk.move_min(hlow, 10, min_count = 5, axis = 0)-bk.move_min(hlow, 25, min_count = 10, axis = 0))
        i12 = bk.move_min(hlow, 20, min_count = 15, axis = 0)-bk.move_min(hlow, 30, min_count = 10, axis = 0)
        i2 = (i11-i12)
        i2 = rolling_norm(i2)[-60:]
        tempdf = np.nansum(i2*mask, axis = 1)
        factor = np.nanmean(tempdf)
        
        return factor
    
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:41:09 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

# 先mask再rolling
class ClMaxClMin_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 9
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close', 'open']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    instrument_type='recent'
    #num_range = '(-0, 1]'
    
    def calculate(self, data):
        
        hclose = data['close_cont_IC'].values[-2000:]
        factor0 = bk.move_max(hclose, 40, min_count = 30)/bk.move_min(hclose, 40, min_count = 30)

        factor1 = rolling_norm(factor0, 242*2)

        factor = bk.move_mean(factor1, 2, min_count = 1)
        
        return factor[-1]
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:44:49 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

# 先mask再rolling
class ICIF1_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close']} 
    #data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 0
    normalize_type = 'ts_rank'
    instrument_type='recent'
    #num_range = '[-0, 1]'
    
    def calculate(self, data):

        hclose = data['close_cont_IC'].iloc[-1345:]
        temp5 = bk.move_mean(hclose, 5, min_count = 2)
        temp10 = bk.move_mean(hclose, 10, min_count = 5)
        temp20 = bk.move_mean(hclose, 20, min_count = 10)
        temp60 = bk.move_mean(hclose, 60, min_count = 30)
        temp120 = bk.move_mean(hclose, 120, min_count = 60)
        
        temp5_diff = (np.diff(temp5)>1e-8).astype(int)
        temp10_diff = (np.diff(temp10)>1e-8).astype(int)
        temp20_diff = (np.diff(temp20)>1e-8).astype(int)
        temp60_diff = (np.diff(temp60)>1e-8).astype(int)
        temp120_diff = (np.diff(temp120)>1e-8).astype(int)
        factor = ts_rank(bk.move_mean(temp5_diff+temp10_diff+temp20_diff+temp60_diff+temp120_diff, 15, min_count = 5))
        factor = np.nanmean(factor[-10:])
        return factor
    
    

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:46:29 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

class LRS_max_CC_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['vwap']} 
    #data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 500
    normalize_type = 'ts_rank'
    instrument_type='recent'
    #num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        vwap = data['vwap_cont_IC'].values[-150:]
        temp1 = bk.move_max(vwap, 50, min_count = 20)
        x = np.array(range(len(vwap)))
        factor = (rolling_linear_reg(x, temp1, 50))
        return factor[-1]
##########
import numpy as np
from future_factor import FutureFactor
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

class wyc_ts19_future_if(FutureFactor):
    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IF':['close', 'high', 'low','volume']}    
    normalize_size = 0 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, df):
        high = df['high_cont_IF'][-1581:]  
        low = df['low_cont_IF'][-1581:]
        close = df['close_cont_IF'][-1581:]
        volume = df['volume_cont_IF'][-1581:]
        a = high - low
        b = (close - low) - (high - close)
        c = b / a * volume
        c = c.replace([np.inf, -np.inf], np.nan)

        factor = bk.move_sum(c.values, 20, 10, axis = 0)[-1561:]
        factor = bk.move_rank(factor, 240, 120, axis = 0)[-1321:]
        factor = bk.move_mean(factor, 120, 60, axis = 0)[-1201:]
        
        factor = rolling_norm(factor, 1200)[-1]

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:55:46 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

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
        s = high.rolling(60, min_periods = 30).std().values
        f = close.rolling(60, min_periods = 30).std().values
        s[abs(s) < 1e-7] = np.nan
        f[abs(f) < 1e-7] = np.nan
        t_chgpcor2 = (high.rolling(60, min_periods=30).cov(close)).values / (s * f)
        t_chgpcor2 = rolling_norm(t_chgpcor2)[-15:]
        tempdf = np.nansum(t_chgpcor2*mask, axis = 1)
        factor = np.nanmean(tempdf)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:57:31 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *



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

##########
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 17:12:17 2021

@author: appadmin
"""

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



class Short_BS_Main_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['amount', 'BuyUniqueOrderNum', 'BuyTradeNum', 'SellUniqueOrderNum', 'SellTradeNum']
    normalize_size = 1200
    normalize_type = 'ts_rank' 

    handle_preadj = False
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-157:]

        stk_BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-126:]
        stk_BuyTradeNum = data['BuyTradeNum'].values[-126:]
        stk_SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-126:]
        stk_SellTradeNum = data['SellTradeNum'].values[-126:]

        df_s = bk.move_sum(stk_amount, 30, 5, axis=0)[-126:]

        
        amount_mask = np.nanquantile(df_s, 0.9, axis=1)
        amount_mask = np.expand_dims(amount_mask, axis=-1)
        factor_raw = (stk_BuyUniqueOrderNum / r(stk_BuyTradeNum)) - (stk_SellUniqueOrderNum / r(stk_SellTradeNum))
        factor_raw_after_mask = ma.array(factor_raw, mask=(df_s<=amount_mask))
        factor_raw_after_mask = np.nanmean(factor_raw_after_mask, axis=1)
        factor_mean = ts_truncated_ema_span_1(factor_raw_after_mask, 120, 4)
        return -factor_mean[-1]
##########
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc8_future_if(FutureFactor):
    data_type = 'Future'
    days_past = 10
    data_dict = dict()
    instrument_type = 'recent'
    # data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Continuous_Data'] = {'IF':['close', 'high', 'low']}
    normalize_size = 1
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        future_close = data['close_cont_IF'].iloc[-2170:]
        future_high = data['high_cont_IF'].iloc[-2170:]
        future_low = data['low_cont_IF'].iloc[-2170:]
        n = 30
        m = 80
        low_n = ts_min(future_low, n)
        high_n = ts_max(future_high, n)
        a = high_n - low_n
        b = (future_close - low_n) / replace_zero(a)
        b_low = ts_min(b, m)
        b_high = ts_max(b, m)
        c = b_high - b_low
        d = (b - b_low) / replace_zero(c)
        e = ts_truncated_ema(d, d=60, alpha=2/3)
        factor_init = ts_truncated_ema(e, d=60, alpha=2/3)
        factor_mean = ts_mean(factor_init, 140)
        factor_raw = ts_rank(factor_mean, 1800)
        return factor_raw[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:48:50 2021

@author: appadmin
"""


import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


class SLHS_CC_ICIF_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 20
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IF':['close', 'high', 'low', 'open']} 
    data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
#    num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        high_spot = (data['high_000905.SH'].values)[-2730:]
        ind = list(range(len(high_spot)))
        m_vwap_ind_r = rolling_linear_reg(ind, high_spot, 60)
        factor = ts_rank(m_vwap_ind_r, 1200)
        factor[factor<=-0.5] = np.nan
        factor = ts_rank(factor, 242*6)
        
        return factor[-1]
    
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:49:55 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *



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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:42:51 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

class HL123_CC_IF(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['close', 'high', 'low', 'open']} 
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
#    num_range = '(-0.5, 1]'
    instrument_type='recent'
    
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
    
##########
from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd
  
class xdy_ts6_spot_tr_if(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = ['close','turnover_rate','adjfactor']
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[0,1]'
    handle_preadj = True
    
    def calculate(self, df):
        close = df['close_preadj'][-465:].values
        gain_close_30 = close[30:]/close[:-30] - 1
        factor = 2 * gain_close_30[20:] - gain_close_30[:-20]
        factor = bk.move_mean(factor, 110, 55, axis = 0)[-305:]
       
        t = df['turnover_rate'][-305:]
        tr = (2 * t.rank(axis=1, pct=True) - 1).values
        factor = factor * tr
        factor = np.nansum(factor, axis=1)

        factor = bk.move_rank(factor, 300, 150, axis = 0)[-5:]
        factor = np.nanmean(factor)

        return factor
##########
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *


class wsc6_cfg_vr_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['stk_volatility', 'close', 'adjfactor']
    normalize_size = 480
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_volatility = data['stk_volatility'].values[-70:]
        stk_close = data['close_preadj'].values[-70:]
        stk_volatility_rank_mask = section_rank_np(stk_volatility, pct=True) * 2 - 1
        stk_ret_short = ts_pct_change(stk_close, 10)
        stk_ret_long = ts_pct_change(stk_close, 60)
        factor_init = stk_ret_long - stk_ret_short
        factor_init[factor_init<0] = 0
        factor_raw = np.nansum(factor_init * stk_volatility_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 10)
        return factor_mean[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:57:14 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


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
##########
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_ma1_if(FutureFactor):
    data_type = 'Future'
    days_past = 3
    data_dict = dict()
    instrument_type = 'recent'
    # data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Continuous_Data'] = {'IF':['close']}
    normalize_size = 0
    normalize_type = 'rolling_norm'
    num_range = None
    
    def calculate(self, data):
        future_close = data['close_cont_IF'].values[-480:]
        close_ma_long = ts_mean(future_close, 120)
        close_ma_short = ts_mean(future_close, 15)
        factor_raw = rolling_norm(close_ma_short-close_ma_long, 360)
        return factor_raw[-1]

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:47:43 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

    
class MALS_ICIF_CC_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IC':['low']} 
    data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 242*2
    normalize_type = 'ts_rank'
#    num_range = '[-0.5, 1]'
    
    def calculate(self, data):
        
        low = data['low_000905.SH'].values[-75:]
        factor = bk.move_mean(low, 75, min_count = 15) - bk.move_mean(shift(low, 15), 60, min_count = 7)
        
        return factor[-1]
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 14:01:18 2021

@author: appadmin
"""


import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


class kpz_ma_displaced_std_zsj_if(FutureFactor):

    data_type = 'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low', 'open']} 
    #data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 0
    normalize_type = 'ts_rank'
    num_range = None
    instrument_type='recent'
    
    def calculate(self, data):
        
        close = data['close_cont_IC'].iloc[-1800:]

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
        factor = bk.move_std(score_raw, 40, min_count = 36, axis = 0)
        factor = bk.move_rank(factor, 242*5, min_count = int(242*5*0.9), axis = 0)[-1]
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:47:09 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


class LminLmean_CC_ICIF_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['low']} 
    #data_dict['Index_Id'] = {'000300.SH':['close', 'high', 'low', 'open']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    instrument_type='recent'
    #num_range = '[-0.8, 1]'
    
    def calculate(self, data):
        
        low = data['low_cont_IC'].values[-60:]
        
        return -np.nanmin(low)/np.nanmean(low[-30:])
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 14:00:50 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

class kpz_dpo_std_zsj_if(FutureFactor):

    data_type = 'Future'
    days_past = 6
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close']} 
    #data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 0
    normalize_type = 'ts_rank'
#    num_range = '(-0.5, 1]'
    instrument_type='recent'
    
    def calculate(self, data):
        
        hclose = data['close_cont_IC'].iloc[-1348:]
        dpo_win = 45
        ma_win = 30
        #ts_pct_win = 1200
        
        def calc_dpo_sig(close, roll_win):
            dpo = close[int(roll_win / 2 + 1):] - REF(MA(close, roll_win), int(roll_win / 2 + 1))
            return dpo   
        
        dpo_raw = calc_dpo_sig(hclose, dpo_win)[-1230:]
        dpo_std_raw = bk.move_std(dpo_raw, 30, min_count = 1, axis = 0)[-1200:]
        dpo_std_raw = bk.move_rank(dpo_std_raw, 1200, 1080, axis = 0)[-1]
        return dpo_std_raw


##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:59:38 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

    
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
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:54:15 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

class L123_at_CFG_CC_IF(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['adjfactor','low','turnover_rate', 'amount']
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
##########
