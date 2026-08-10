# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 15:06:14 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator


class HHLS_ind_ICIF_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns=['high_spot','recent_month_mask']

        super(HHLS_ind_ICIF_CC_IF, self).__init__(required_columns=required_columns)
    

    

    
    def on_bar(self, data):

        temp = data['high_spot'].rolling(50, min_periods = 15).max() - data['high_spot'].shift(50).rolling(50, min_periods = 7).max()
        factor = temp.to_frame()

        #factor = np.abs(factor)

        factor = rolling_norm(factor)
        factor[factor<-1] = 0
        factor[factor>1] = 0
        factor.columns = [self.__class__.__name__]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 14:28:58 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator


class L123_ind_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns=['low_spot_if']

        super(L123_ind_CC_IF, self).__init__(required_columns=required_columns)
    

    

    
    def on_bar(self, df):
        columnname = self.__class__.__name__
        hlow = df['low_spot_if']
        i11 = (hlow.rolling(10, min_periods = 5).min()-hlow.rolling(25, min_periods = 10).min())
        i12 = hlow.rolling(20, min_periods = 15).min()-hlow.rolling(30, min_periods = 10).min()
        i2 = (i11-i12).rolling(60, min_periods = 2).mean()
        i2 = ts_rank(i2.to_frame())
        i2.columns = [columnname]    
        return i2
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 09:16:03 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class HDLD_ae_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_hs300','turnover_hs300', 'weight_boolean_hs300', 'close_hs300', 'open_hs300']

        super(HDLD_ae_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, data):
        df_s = (data['amount_hs300'].rolling(120, min_periods = 15).sum())[data['weight_boolean_hs300']]
        ret_30 = (data['turnover_hs300']/data['turnover_hs300'].shift(30)-1)[data['weight_boolean_hs300']]
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0)
        temp5 = ret_30.gt(pd.Series(ret_30.quantile(0.80, axis = 1)), axis=0)
        mask = temp1*temp5
        temp1 = pd.DataFrame(np.where(data['open_hs300']>data['close_hs300'], data['open_hs300'], data['close_hs300']))
        temp2 = pd.DataFrame(np.where(data['open_hs300']>data['close_hs300'], data['close_hs300'], data['open_hs300']))
        temp1.index = data['open_hs300'].index
        temp2.index = data['open_hs300'].index
        temp1.columns = data['open_hs300'].columns
        temp2.columns = data['open_hs300'].columns
        t_pcorr = (temp1.diff()+temp2.diff())

        tempdf = (t_pcorr*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(60, min_periods = 30).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np


class wyc_ts44_future_if(FactorGenerator):
    def __init__(self):
        required_columns = ['volume_if', 'close_if', 'recent_month_mask']
        lookback_bars = 2000
        super(wyc_ts44_future_if, self).__init__(
            required_columns=required_columns,
            lookback_bars=lookback_bars)

    def on_bar(self, df):
        temp1 = df['volume_if'].copy(deep=True)
        con1 = df['close_if'] > delay(df['close_if'], 1)
        con2 = df['close_if'] < delay(df['close_if'], 1)
        temp1[con2] = -1 * df['volume_if']
        factor = ts_sum(temp1, 15)
        factor = mean(factor, 60)
        mask = df['recent_month_mask']
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor < 0] = 0
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 10:53:44 2021

@author: appadmin
"""
import pandas as pd
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *
import numpy as np

class CFG7_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_hs300','open_hs300', 'weight_boolean_hs300', 'close_hs300', 'turnover_hs300', 'weight_boolean_hs300']

        super(CFG7_CC_IF, self).__init__(required_columns=required_columns
                                  )
        
    def on_bar(self, df):
        columnname = self.__class__.__name__
        to = df['turnover_hs300']
        hclose = df['close_hs300']
        
        hopen = df['open_hs300']
        ret = hclose/hopen -1
        hret = hclose/hclose.shift(1) -1
        ret = ret.replace([np.inf, -np.inf], np.nan)
        hret = hret.replace([np.inf, -np.inf], np.nan)
        cc1 = ((to[hclose<hopen]/abs(ret[hclose<hopen])))
        cc1[abs(cc1) > 100000] = np.nan
        ccc1 = cc1.rolling(90, min_periods = 7).mean()
        ccc1 = ccc1[df['weight_boolean_hs300']]
        hret = hret[df['weight_boolean_hs300']]
        cc2 = to_ts(ccc1, hret)
        ccc2 = cc2.rolling(90, min_periods = 15).mean()
        cc3 = rolling_norm(ccc2.to_frame(), method = 'ts_rank')
        #cc3 = cc3.rolling(3, min_periods = 2).mean()
        cc3[cc3<=-1] = np.nan
        cc3[cc3>1] = np.nan
        cc3.columns = [columnname]
        return cc3
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 16 13:32:45 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class L123_nr_vt_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['turnover_hs300', 'weight_boolean_hs300', 'close_hs300', 'low_hs300',]
        super(L123_nr_vt_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, df):
        stk_close = df['close_hs300']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = ts_std(stk_ret, 30)
        stk_volatility = stk_volatility[df['weight_boolean_hs300']]
        turnover = (df['turnover_hs300'].rolling(60, min_periods = 15).mean())[df['weight_boolean_hs300']]
        temp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0)
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)    
        mask = temp3*temp4
        
        hlow = df['low_hs300']
        i11 = (hlow.rolling(10, min_periods = 5).min()-hlow.rolling(25, min_periods = 10).min())
        i12 = hlow.rolling(20, min_periods = 15).min()-hlow.rolling(30, min_periods = 10).min()
        ctl_r = (i11-i12)
        ctl_r = rolling_norm(ctl_r, 242*5)
        ctl_r[np.abs(ctl_r)>1] = np.nan
        tempdf = (ctl_r*mask)
        tempdf = tempdf.mean(axis = 1).to_frame()
        factor = tempdf.rolling(40, min_periods = 2).mean()
        factor = ts_rank(factor, 720)
        
        factor.columns = [self.__class__.__name__]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 13:57:11 2020

@author: appadmin
"""

import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex

class HL123_nr_av_CC_CFG_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_boolean_hs300', 'amount_hs300', 'close_hs300', 'high_hs300', 'low_hs300']

        super(HL123_nr_av_CC_CFG_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

  
    def on_bar(self, data):
        df_s = (data['amount_hs300'].rolling(120, min_periods = 15).sum())[data['weight_boolean_hs300']]
        stk_close = data['close_hs300']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = ts_std(stk_ret, 30)
        stk_volatility = stk_volatility[data['weight_boolean_hs300']]
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0)
        temp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0)
        mask = temp3*temp1
        hlow = data['low_hs300']
        hhigh = data['high_hs300']
        i11 = hhigh.rolling(10, min_periods = 5).max()-hlow.rolling(60, min_periods = 10).min()
        i12 = (hhigh.shift(30)).rolling(10, min_periods = 5).max()-(hlow.shift(30)).rolling(60, min_periods = 10).min()
        i2 = (i11-i12)
        i2 = rolling_norm(i2, 242*5)
        tempdf = (i2*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(30, min_periods = 15).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 11:13:43 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex

class LminLmean_nr_as_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_hs300', 'weight_boolean_hs300', 'low_hs300']

        super(LminLmean_nr_as_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, df):
        df_s = (df['amount_hs300'].rolling(120, min_periods = 15).sum())[df['weight_boolean_hs300']]
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)   
        mask = stk_amount
        
        ctl_r = -df['low_hs300'].rolling(60, min_periods =15).min()/df['low_hs300'].rolling(30, min_periods =10).mean()
        lltc_ind_r = rolling_norm(ctl_r)
        tempdf = (lltc_ind_r*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(8, min_periods = 4).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


def delta(df1, d):
    # A_(i-d)
    output = df1.diff(periods=d)
    return output


def ts_max(df1, d):
    # time-series max over the past d periods.
    output = pd.DataFrame(bk.move_max(df1, window=d, min_count=int(d / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


class wsc_search5_long_if(FactorGenerator):
    def __init__(self):
        super(wsc_search5_long_if, self).__init__(required_columns=['close', 'recent_month_mask'],
                                                  lookback_bars=2000)

    def on_bar(self, data):
        # 算法搜索
        mask = data['recent_month_mask']
        close = data['close']
        factor1 = delta(close, 25)
        factor = ts_max(factor1, 25)
        factor = rolling_norm(factor, 1200)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor <= -0.5] = 0
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator import FactorGenerator
from operators_wsc import *



class wsc_1_spot_if(FactorGenerator):
    def __init__(self):
        super(wsc_1_spot_if, self).__init__(required_columns=['close_spot_if', 'volume_spot_if'],
                                            lookback_bars=2000)

    def on_bar(self, data):
        # 长江金工高频因子2：结构化反转因子
        # 因子主体由三部分组成：对数收益率，成交量倒数和收益波动率
        # 对数收益率代表动量，成交量倒数的逻辑是当多空力量悬殊时，股价会以很小的成交量迅速到达一个合理价位（这部分内容见研报），收益波动率的逻辑是只有当市场成交活跃时，趋势才强
        index_close = data['close_spot_if']
        index_volume = data['volume_spot_if']
        ret = ts_pct_change(index_close, 1)
        log_ret = log(ret+1)
        ret_std = ts_std(ret, 15)
        log_ret_weight = log_ret / index_volume * ret_std
        factor_raw = ts_sum(log_ret_weight, 120)
        factor_mean = ts_mean(factor_raw, 1)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = np.nan
        #factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 10:31:33 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
import bottleneck as bk

class ICIF2_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns=['close_spot']

        super(ICIF2_CC_IF, self).__init__(required_columns=required_columns)
        
    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
        
    def on_bar(self, data):
        columnname = self.__class__.__name__
        ret = data['close_spot']/data['close_spot'].shift(1)-1
        i1 = (data['close_spot']/data['close_spot'].shift(24)-1) / ret.rolling(25, min_periods = 15).std()
        i1 = i1.to_frame()
        i2 = self.ts_rank(i1.rolling(20, min_periods = 2).mean())
        i2[i2>1] = 0
        i2[i2<=-0.5] = 0
        i2.columns = [columnname]    
        return i2
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 17:41:08 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class LSC_CC_ICIF_IF(FactorGenerator):
    def __init__(self):

        required_columns =['high', 'low', 'close', 'recent_month_mask']

        super(LSC_CC_ICIF_IF, self).__init__(
                                  required_columns=required_columns)

    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa
        
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa  
        
    def on_bar(self, data):

        hh = (data['high'].rolling(30, min_periods = 10).max() - data['close'])/(data['high'].rolling(30, min_periods = 10).max() - data['low'].rolling(30, min_periods = 10).min()) 
        ll = (data['close'] - data['low'].rolling(30, min_periods = 10).min())/(data['high'].rolling(30, min_periods = 10).max() - data['low'].rolling(30, min_periods = 10).min())
        vwtc_r = ll.rolling(30, min_periods = 15).mean()-hh.rolling(30, min_periods = 15).mean()
        factor = vwtc_r[data['recent_month_mask']].mean(axis = 1).to_frame()

        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        factor[factor<=-0.5] = np.nan
        factor = self.ts_rank(factor)
        factor[factor<=-0.5] = 0
        return factor

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    return rolling_table


def reg_beta(df1, d):
    # 过去d期A对1:d回归的回归系数
    output = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
    for i in df1.columns:
        temp_y = df1[i].values
        temp_y = rolling_window(temp_y, d)
        temp_x = np.tile(np.arange(d) + 1, (temp_y.shape[0], 1))
        y = np.nansum((temp_y.T - np.nanmean(temp_y, axis=1).T) * (temp_x.T - np.nanmean(temp_x, axis=1).T), axis=0)
        x = np.nansum((temp_x.T - np.nanmean(temp_x, axis=1).T) ** 2, axis=0)
        flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
        flag = np.where(flag <= d - int(d / 2), 1, np.nan)
        output[i].iloc[d - 1:] = (y / x) * flag
    return output


class wsc_mean_plus_std_if(FactorGenerator):
    def __init__(self):
        super(wsc_mean_plus_std_if, self).__init__(required_columns=['close_spot'],
                                                lookback_bars=2000)

    def on_bar(self, data):
        # 计算过去5分钟收益率的均值和标准差的线性组合
        a = data['close_spot'].pct_change(5, fill_method=None)
        b = a.rolling(30, min_periods=15).mean()
        c = a.rolling(30, min_periods=15).std()
        factor = b + 2 * c
        factor = factor.rolling(10).mean()
        # factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = ts_rank(factor, 600*2)
        # factor[factor <= -0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator import FactorGenerator
from operators_wyc import *

class wyc_ts38_icfuture_if(FactorGenerator):
    def __init__(self):

        required_columns=['close', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts38_icfuture_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        smaM = 80
        stdN = 120
        temp1 = df['close'].copy()
        temp1[df['close'] > delay(df['close'], 1)] = std(df['close'], stdN)
        temp1[df['close'] <= delay(df['close'], 1)] = 0
        a = sma(temp1, smaM, 1)
        temp1[df['close'] > delay(df['close'], 1)] = 0
        temp1[df['close'] <= delay(df['close'], 1)] = std(df['close'], stdN)
        b = sma(temp1, smaM, 1)
        c = a + b
        c[abs(c) < 1e-8] = np.nan
        factor = a / c * 100
        factor = ts_rank(factor, 30)
        factor = ts_mean(factor, 50)
        mask = df['recent_month_mask']
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()
        
        factor.columns = [columnname]
        factor[factor >= 0.5] = 0

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 15:25:37 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator

class RolTrendLS_ind_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot', 'low_spot', 'high_spot']

        super(RolTrendLS_ind_CC_IF, self).__init__(
                                  required_columns=required_columns)
        


    def on_bar(self, data):

        ll = (data['close_spot'] - data['low_spot'].rolling(60, min_periods = 15).min())/(data['high_spot'].rolling(60, min_periods = 15).max() - data['low_spot'].rolling(60, min_periods = 15).min())
        a2 = ll.rolling(10, min_periods = 5).mean()
        a3 = a2.rolling(10, min_periods = 5).mean()
        vwtc_r = 3*a3-2*a2
        factor = vwtc_r.rolling(5, min_periods = 2).mean().to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        return factor
    
##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc6_cfg_ws_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc6_cfg_ws_if, self).__init__(required_columns=['close_hs300', 'weight_hs300'],
                                             lookback_bars=2000)

    def on_bar(self, data):
        #mask
        stk_weight = data['weight_hs300']

        # 计算长短期收益率之差，并只保留大于0的部分
        stk_close = data['close_hs300']
        stk_ret_short = ts_pct_change(stk_close, 10)
        stk_ret_long = ts_pct_change(stk_close, 60)
        factor_init = stk_ret_long - stk_ret_short
        factor_init[factor_init<0] = 0
        factor_raw = (factor_init * stk_weight).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 5)
        factor = ts_rank(factor_mean, 240*2)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 16:42:14 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator

class HLTM_Aug_ind_ICIF_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot', 'high_spot', 'low_spot', 'volume_spot']

        super(HLTM_Aug_ind_ICIF_CC_IF, self).__init__(
                                  required_columns=required_columns)


    def on_bar(self, data):

        temp1 = data['high_spot'].rolling(15, min_periods = 7).max()-data['close_spot']
        temp2 = data['close_spot']-data['low_spot'].rolling(15, min_periods = 7).min()
        temp = pd.Series(np.where(temp1>temp2, temp1, temp2))
        temp.index = data['high_spot'].index
        vwtc_r = (temp*data['volume_spot']).rolling(35, min_periods = 10).mean()
        
        factor = vwtc_r.to_frame()
        

        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor, 242*5)
        return factor

##########
from factor_generator import FactorGenerator
from operators_wyc import *

class wyc_ts32_icfuture_if(FactorGenerator):
    def __init__(self):

        required_columns=['close', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts32_icfuture_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        temp = df['close'].copy()
        N = 20
        UP = temp.copy(deep=True)
        UP[df['close'] > delay(df['close'], 1)] = std(df['close'], N)
        UP[df['close'] <= delay(df['close'], 1)] = 0
        factor = multi_processing_joblib(df=UP, func=ts_truncated_ema, n_jobs=-1, d=60, alpha= 1/10)
        factor = ts_rank(factor, 2 * 242)
        factor = ts_mean(factor, 20)
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 5 * 242)
        mask = df['recent_month_mask']
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        factor.columns = [columnname]

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 14:40:40 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class SYXWR_nr_wt_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['turnover_hs300', 'weight_boolean_hs300', 'weight_hs300', 'low_hs300', 'high_hs300', 'turnover_hs300','open_hs300', 'close_hs300']
        super(SYXWR_nr_wt_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, data):
        turnover = (data['turnover_hs300'].rolling(60, min_periods = 15).mean())[data['weight_boolean_hs300']]
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)
        stk_weight = (data['weight_hs300'])[data['weight_boolean_hs300']]        
        mask = stk_weight*temp4
        temp1 = pd.DataFrame(np.where(data['open_hs300']>data['close_hs300'], data['open_hs300'], data['close_hs300']))
        temp2 = pd.DataFrame(np.where(data['open_hs300']>data['close_hs300'], data['close_hs300'], data['open_hs300']))
        temp1.index = data['open_hs300'].index
        temp2.index = data['open_hs300'].index
        temp1.columns = data['open_hs300'].columns
        temp2.columns = data['open_hs300'].columns
        b = (data['high_hs300'] - temp1).rolling(30, min_periods = 15).mean()
        b[abs(b)<1e-8] = np.nan
        t_pcor = (data['high_hs300']-temp1)/b
        a = (data['high_hs300'].rolling(30, min_periods = 15).max()-data['low_hs300'].rolling(30, min_periods = 15).min())
        a[abs(a) < 1e-8] = np.nan
        t_pcor2 = (data['close_hs300']-data['low_hs300'].rolling(30, min_periods = 15).min())/a
        t_pcorr = (t_pcor2 - t_pcor)
        tempdf = (t_pcorr*mask).sum(axis = 1).to_frame()
        
        factor = rolling_norm(tempdf, 242*5)
        factor[abs(factor)>1] = np.nan
        
        factor = tempdf.rolling(45, min_periods = 10).mean()
        factor = ts_rank(factor) 
        factor.columns = [self.__class__.__name__]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 15:07:04 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator

class Crossing_Turns_ICIF_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['open', 'low', 'close', 'high', 'vwap','recent_month_mask']

        super(Crossing_Turns_ICIF_CC_IF, self).__init__(
                                  required_columns=required_columns)
    

    
    def on_bar(self, data):

        temp = np.abs(pd.DataFrame(np.where(data['open']-data['close'] == 0, 0.1, data['open']-data['close'])))
        temp.index = data['open'].index
        temp.columns = data['open'].columns
        temp0 = (data['high'] - data['low'])

        temp1 = temp0/temp
        temp1 = temp1.replace([-np.inf, np.inf], np.nan)
        a = (data['vwap']/data['vwap'].shift(1)-1).rolling(30, min_periods = 15).sum()
        vwtc_r = (temp1*(a)).rolling(25, min_periods = 5).mean()
        factor = vwtc_r[data['recent_month_mask']].mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor, 242*3)
        factor = factor.rolling(2, min_periods = 2).mean()
        factor[factor<=-0.5]=np.nan
        factor = ts_rank(factor)
        factor[factor<=-0.5]=0
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc3_cfg_ar_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc3_cfg_ar_if, self).__init__(required_columns=['close_hs300', 'open_hs300', 'high_hs300', 'low_hs300', 'weight_boolean_hs300', 'amount_hs300'],
                                             lookback_bars=2000)

    def on_bar(self, data):
        # mask
        bool_mask = data['weight_boolean_hs300']
        amount_mask = data['amount_hs300'][bool_mask]
        amount_rank_mask = 2 * amount_mask.rank(axis=1, pct=True) - 1

        # 用(close-open)/(high-low)衡量当下分钟的股价波动
        stk_close = data['close_hs300']
        stk_open = data['open_hs300']
        stk_high = data['high_hs300']
        stk_low = data['low_hs300']
        a = stk_high - stk_low
        a[abs(a)<1e-5] = np.nan
        b = stk_close - stk_open
        b[b<0] = np.nan
        factor_init = ts_sum(b/a, 60)
        factor_raw = (factor_init * amount_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *
from joblib import Parallel, delayed



def ts_reg_beta1(df1, d):
    output = pd.Series(np.nan, index=df1.index, name=df1.name)
    temp_y = df1.values
    temp_y = rolling_window(temp_y, d)
    temp_x = np.tile(np.arange(d) + 1, (temp_y.shape[0], 1))
    y = np.nansum((temp_y.T - np.nanmean(temp_y, axis=1).T) * (temp_x.T - np.nanmean(temp_x, axis=1).T), axis=0)
    x = np.nansum((temp_x.T - np.nanmean(temp_x, axis=1).T) ** 2, axis=0)
    flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
    flag = np.where(flag <= d - int(d / 2), 1, np.nan)
    output.iloc[d - 1:] = (y / x) * flag
    return output

# 成分股因子截面切割多进程
def multi_processin_joblib(df, func, n_jobs=12, **kwargs):
    results = Parallel(n_jobs=n_jobs)(delayed(func)(df[i], **kwargs) for i in df.columns)
    results_df = pd.DataFrame(results, index=df.columns, columns=df.index)
    return results_df.T


class wsc12_cfg_search_vs_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc12_cfg_search_vs_if, self).__init__(required_columns=['close_hs300', 'stk_volatility_hs300'],
                                                     lookback_bars=2000)

    def on_bar(self, data):
        # mask
        volatility_mask = data['stk_volatility_hs300']

        # 算子搜索
        stk_close = data['close_hs300']
        factor_init = multi_processin_joblib(stk_close, ts_reg_beta1, 16, d=40)
        factor_raw = (factor_init * volatility_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 5)
        factor = ts_rank(factor_mean, 240*5)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 16 14:22:15 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

 
from factor_generator_complex import FactorGeneratorComplex

class ZHZH_vt_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['turnover_hs300', 'close_hs300', 'weight_boolean_hs300', 'high_hs300']
        super(ZHZH_vt_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, data):
        
        turnover = (data['turnover_hs300'].rolling(60, min_periods = 15).mean())[data['weight_boolean_hs300']]
        stk_close = data['close_hs300']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = ts_std(stk_ret, 30)
        stk_volatility = stk_volatility[data['weight_boolean_hs300']]
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0) 
        temp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0)
        mask = temp3*temp4
        
        temp = (data['high_hs300']>=(data['high_hs300'].rolling(10, min_periods = 5).max())).astype(int).rolling(90, min_periods = 5).mean()
        
        tempdf = (temp*mask)
        tempdf = tempdf.mean(axis = 1).to_frame()
        factor = tempdf.rolling(15, min_periods = 8).mean()
        factor = ts_rank(factor)
        
        factor.columns = [self.__class__.__name__]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 16:48:03 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator


# demo
class hhll_ind_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['high_spot_if', 'low_spot_if','recent_month_mask']

        super(hhll_ind_CC_IF, self).__init__(
                                  required_columns=required_columns)



    def on_bar(self, data):

        temp = np.where((data['high_spot_if']>data['high_spot_if'].shift(1)) & (data['low_spot_if']>data['low_spot_if'].shift(1)), 4, np.where((data['high_spot_if']<data['high_spot_if'].shift(1)) & (data['low_spot_if']<data['low_spot_if'].shift(1)), 0, 1))
        temp = pd.Series(temp)
        temp.index = data['high_spot_if'].index
        vwtc_r = temp.rolling(120, min_periods =10).mean()
        factor = vwtc_r.to_frame()
        factor = np.abs(factor)
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        factor[factor<=-0.5] = 0
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *
from joblib import Parallel, delayed



def ts_reg_beta1(df1, d):
    output = pd.Series(np.nan, index=df1.index, name=df1.name)
    temp_y = df1.values
    temp_y = rolling_window(temp_y, d)
    temp_x = np.tile(np.arange(d) + 1, (temp_y.shape[0], 1))
    y = np.nansum((temp_y.T - np.nanmean(temp_y, axis=1).T) * (temp_x.T - np.nanmean(temp_x, axis=1).T), axis=0)
    x = np.nansum((temp_x.T - np.nanmean(temp_x, axis=1).T) ** 2, axis=0)
    flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
    flag = np.where(flag <= d - int(d / 2), 1, np.nan)
    output.iloc[d - 1:] = (y / x) * flag
    return output

# 成分股因子截面切割多进程
def multi_processin_joblib(df, func, n_jobs=12, **kwargs):
    results = Parallel(n_jobs=n_jobs)(delayed(func)(df[i], **kwargs) for i in df.columns)
    results_df = pd.DataFrame(results, index=df.columns, columns=df.index)
    return results_df.T


class wsc12_cfg_search_ws_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc12_cfg_search_ws_if, self).__init__(required_columns=['close_hs300', 'weight_hs300'],
                                                     lookback_bars=3000)

    def on_bar(self, data):
        # mask
        stk_weight = data['weight_hs300']

        # 算子搜索
        stk_close = data['close_hs300']
        factor_init = multi_processin_joblib(stk_close, ts_reg_beta1, 16, d=40)
        factor_raw = (factor_init * stk_weight).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 45)
        factor = ts_rank(factor_mean, 240*5)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 09:54:29 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
import numpy as np
from factor_generator import FactorGenerator

class ZHZH_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['high_if', 'recent_month_mask']

        super(ZHZH_CC_IF, self).__init__(
                                  required_columns=required_columns)

    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa

    
    def on_bar(self, data):

        temp = (data['high_if']>=(data['high_if'].rolling(10, min_periods = 5).max())).astype(int).rolling(120, min_periods = 5).mean()
        factor = self.ts_rank(temp[data['recent_month_mask']].mean(axis = 1).to_frame())
        #factor = self.ts_rank(factor)
        factor[factor<=-0.5] = 0
        factor.columns = [self.__class__.__name__]
        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc7_cfg_cr_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc7_cfg_cr_if, self).__init__(required_columns=['close_hs300', 'stk_index_corr_hs300'],
                                             lookback_bars=2000)

    def on_bar(self, data):
        # mask
        corr_mask = data['stk_index_corr_hs300']
        corr_rank_mask = 2 * corr_mask.rank(axis=1, pct=True) - 1

        # as follows
        stk_close = data['close_hs300']
        stk_ret = ts_pct_change(stk_close, 5)
        b = ts_mean(stk_ret, 30)
        c = ts_std(stk_ret, 30)
        factor_init = b + c
        factor_raw = (factor_init * corr_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        factor = ts_rank(factor_mean, 240*10)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 10:09:00 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class hhll_nr_we_CC_CFG_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_hs300','turnover_hs300', 'weight_boolean_hs300', 'close_hs300', 'high_hs300', 'low_hs300']

        super(hhll_nr_we_CC_CFG_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, data):
        ret_30 = (data['turnover_hs300']/data['turnover_hs300'].shift(30)-1)[data['weight_boolean_hs300']]
        temp5 = ret_30.gt(pd.Series(ret_30.quantile(0.80, axis = 1)), axis=0)
        stk_weight = (data['weight_hs300'])[data['weight_boolean_hs300']]
        mask = temp5*stk_weight
        temp1 = (data['high_hs300']>data['high_hs300'].shift(1)).astype(int)
        temp2 = (data['low_hs300']>data['low_hs300'].shift(1)).astype(int)
        
        temp =  temp1+temp2
        temp[temp==2] = 4
        temp = rolling_norm(temp, 242*5)
        tempdf = (temp*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(60, min_periods = 30).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 16:07:46 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


import numpy as np
from factor_generator import FactorGenerator

# 多头因子
class cd_ind_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns =['close_spot_if']
        
        super(cd_ind_CC_IF, self).__init__(
                                  required_columns=required_columns)
        
    def on_bar(self, data):

        temp = data['close_spot_if'].rolling(60, min_periods = 2).mean().diff()
        factor = temp.to_frame()
        factor.columns =  [self.__class__.__name__]
        factor = rolling_norm(factor, 4800)
        factor[factor<0] = 0
        factor[factor>1] = 0
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc2_cfg_ws_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc2_cfg_ws_if, self).__init__(required_columns=['close_hs300', 'open_hs300', 'weight_hs300', 'volume_hs300'],
                                             lookback_bars=2000)

    def on_bar(self, data):
        # 假设持仓30分钟，min_30_earning表示那一分钟这笔持仓的盈亏
        stk_close = data['close_hs300']
        stk_open = data['open_hs300']
        stk_weight = data['weight_hs300']
        stk_volume = data['volume_hs300']
        factor_init = (stk_close - stk_open.shift(30)) * stk_volume
        factor_raw = (factor_init * stk_weight).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 20)
        factor = ts_rank(factor_mean, 1200)
        factor[factor<=-0.5] = 0
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np


class wyc_ts7_future_vr_if(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_hs300'

        required_columns=['close' + suffix, 'stk_volatility' + suffix]
        lookback_bars=2000
        super(wyc_ts7_future_vr_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_hs300'
        columnname = self.__class__.__name__

        N = 15
        logclose = log(df['close' + suffix])
        s1 = multi_processing_joblib(df=logclose, func=ts_truncated_ema, n_jobs=-1, d=60, alpha= 2/N)
        s2 = multi_processing_joblib(df=s1, func=ts_truncated_ema, n_jobs=-1, d=60, alpha= 2/N)
        s3 = multi_processing_joblib(df=s2, func=ts_truncated_ema, n_jobs=-1, d=60, alpha= 2/N)
        s3[abs(s3) < 1e-8] = np.nan
        factor = s3 / delay(s3, 1) - 1
        
        factor = ts_mean(factor, 10)

        vr = (2 * df['stk_volatility' + suffix].rank(axis=1, pct=True) - 1)
        factor = factor * vr
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 13:14:43 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator


class ICIF4_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns=['close_spot']

        super(ICIF4_CC_IF, self).__init__(required_columns=required_columns)

    

    
    def on_bar(self, data):

        temp = data['close_spot'].rolling(60, min_periods = 15).mean() - data['close_spot'].shift(20).rolling(40, min_periods = 7).mean()
        factor = temp.to_frame()

        factor = np.abs(factor)

        factor = ts_rank(factor)

        factor[factor<=-0.5] = 0
        factor.columns = [self.__class__.__name__]
        return factor
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    return rolling_table


def reg_beta(df1, d):
    # 过去d期A对1:d回归的回归系数
    output = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
    for i in df1.columns:
        temp_y = df1[i].values
        temp_y = rolling_window(temp_y, d)
        temp_x = np.tile(np.arange(d) + 1, (temp_y.shape[0], 1))
        y = np.nansum((temp_y.T - np.nanmean(temp_y, axis=1).T) * (temp_x.T - np.nanmean(temp_x, axis=1).T), axis=0)
        x = np.nansum((temp_x.T - np.nanmean(temp_x, axis=1).T) ** 2, axis=0)
        flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
        flag = np.where(flag <= d - int(d / 2), 1, np.nan)
        output[i].iloc[d - 1:] = (y / x) * flag
    return output


def ts_sma(df1, alpha):
    # 移动平均 Y_0 = A_0, Y_i = alpha*A_i + (1-alpha)*Y_(i-1)
    output = df1.ewm(alpha=alpha, adjust=False).mean()
    return output


class wsc6_future_kpz_if(FactorGenerator):
    def __init__(self):
        super(wsc6_future_kpz_if, self).__init__(required_columns=['close', 'recent_month_mask'],
                                                 lookback_bars=2000)

    def on_bar(self, data):
        # 算子搜索
        mask = data['recent_month_mask']
        data_need = data['close']
        factor = reg_beta(data_need, 80)
        factor = rolling_norm(factor, 650)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor <= -0.5] = 0
        # factor[factor>=0.5] = np.nan
        return factor

##########
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np
from functools import partial
from joblib import Parallel, delayed


def place_back_format(dat_mat, dat_orig):
    if isinstance(dat_orig, pd.DataFrame):
        dat_fmt = pd.DataFrame(dat_mat, index=dat_orig.index, columns=dat_orig.columns)
    elif isinstance(dat_orig, pd.Series):
        dat_fmt = pd.Series(dat_mat, index=dat_orig.index)
        dat_fmt.name = dat_orig.name
    else:
        dat_fmt = dat_mat
    return dat_fmt


def calc_ts_pct(ts_dat, roll_win=20, min_pct=1, force_range=False):
    min_win = int(min_pct * roll_win)
    ts_dat_pct_np = bk.move_rank(ts_dat, window=roll_win, min_count=min_win, axis=0)
    if force_range:
        ts_dat_pct_np = (ts_dat_pct_np + 1) / 2
    ts_dat_pct = place_back_format(ts_dat_pct_np, ts_dat)
    return ts_dat_pct


def calc_change_helper(score_raw, short_win, long_win, ts_pct_win, sign=1, min_pct=0.9):
    score_change_raw = sign * (
            score_raw.rolling(short_win, int(min_pct * short_win)).mean() - score_raw.rolling(long_win, int(
        min_pct * long_win)).mean())
    score_change = calc_ts_pct(score_change_raw, ts_pct_win, min_pct=min_pct)
    return score_change


def calc_std_helper(score_raw, std_win, ts_pct_win, min_pct=0.9):
    score_std_raw = score_raw.rolling(std_win, int(min_pct * std_win)).std()
    score_std = calc_ts_pct(score_std_raw, ts_pct_win)
    return score_std


def calc_ma_helper(score_raw, ma_win, ts_pct_win, min_pct=0.9):
    score_ma_raw = score_raw.rolling(ma_win, int(min_pct * ma_win)).mean()
    score_ma = calc_ts_pct(score_ma_raw, ts_pct_win, min_pct=min_pct)
    return score_ma


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


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


def multi_processing_joblib(df, func, n_jobs, **kwargs):
    results = Parallel(n_jobs=n_jobs)(delayed(func)(df[i], **kwargs) for i in df.columns)
    results_df = pd.DataFrame(results, index=df.columns, columns=df.index)
    return results_df.T


class stk2idx_maxret_diff_chg_zsj_if(FactorGeneratorComplex):
    def __init__(self):
        super(stk2idx_maxret_diff_chg_zsj_if, self).__init__(required_columns=['close_hs300', 'amount_hs300', 'weight_boolean_hs300'],
                                                             lookback_bars=2000)

    def on_bar(self, data):
        ## prep data
        bool_mask = data['weight_boolean_hs300']
        stk_close = data['close_hs300']
        stk_amt = data['amount_hs300']
        stk_close[abs(stk_close) < 1e-8] = np.nan
        stk_ret = stk_close / stk_close.shift(1) - 1

        ret_win = 60
        stk_max_ret = multi_processing_joblib(df=stk_ret, func=get_top_mean, n_jobs=20, d=ret_win)

        # common code for maxret_diff
        ret_win_short = 5
        stk_ret_duration = stk_close/stk_close.shift(ret_win_short) - 1 
        stk_maxret_diff = stk_max_ret - (stk_ret_duration/ret_win_short)
        stk_maxret_diff[~np.isfinite(stk_maxret_diff)] = np.nan
        stk2idx_maxret_diff_raw = stk_maxret_diff[bool_mask].mean(axis=1)

        # factor logic
        short_win = 10
        long_win = 35
        ts_pct_win = 1200
        min_pct = 0.9
        stk2idx_maxret_diff_chg = calc_change_helper(stk2idx_maxret_diff_raw,short_win,long_win,ts_pct_win)
        factor = stk2idx_maxret_diff_chg.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 16:06:43 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator import FactorGenerator

class VMaxVmean_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns=['vwap', 'recent_month_mask']
        super(VMaxVmean_CC_IF, self).__init__(required_columns=required_columns)

        


    def on_bar(self, data):

        m_vwap_r = data['vwap'].rolling(60, min_periods = 30).max()/data['vwap'].rolling(60, min_periods = 30).min()
        factor = m_vwap_r[data['recent_month_mask']].mean(axis = 1).to_frame()

        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor, 480)
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 14:31:16 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator import FactorGenerator

class LminLmean_ind_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns =['low_spot_if']
        super(LminLmean_ind_CC_IF, self).__init__(
                                  required_columns=required_columns)
    


    def on_bar(self, data):

        ctl_r = -data['low_spot_if'].rolling(45, min_periods =30).min()/data['low_spot_if'].rolling(25, min_periods =15).mean()
        factor = ctl_r.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        return factor

##########
from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np


def rolling_normalize(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


class xdy_ts1_future_if(FactorGenerator):
    def __init__(self):
        required_columns = ['high_if', 'close_if', 'recent_month_mask']
        lookback_bars = 2000
        super(xdy_ts1_future_if, self).__init__(required_columns=required_columns,
                                                lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        high = df['high_if']
        close = df['close_if']
        gain_high_60 = high / high.shift(100) - 1
        h_c = close / high - 1
        a = mean(h_c, 60)
        a[abs(a) < 1e-8] = np.nan
        factor = ts_sum(gain_high_60 / a, 5)
        factor = mean(factor, 10) * -1
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 3 * 242)
        mask = df['recent_month_mask']
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor[factor <= -0.5] = 0

        return factor

##########
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np


def place_back_format(dat_mat, dat_orig):
    if isinstance(dat_orig, pd.DataFrame):
        dat_fmt = pd.DataFrame(dat_mat, index=dat_orig.index, columns=dat_orig.columns)
    elif isinstance(dat_orig, pd.Series):
        dat_fmt = pd.Series(dat_mat, index=dat_orig.index)
        dat_fmt.name = dat_orig.name
    else:
        dat_fmt = dat_mat
    return dat_fmt


def calc_ts_pct(ts_dat, roll_win=20, min_pct=1, force_range=False):
    min_win = int(min_pct * roll_win)
    ts_dat_pct_np = bk.move_rank(ts_dat, window=roll_win, min_count=min_win, axis=0)
    if force_range:
        ts_dat_pct_np = (ts_dat_pct_np + 1) / 2
    ts_dat_pct = place_back_format(ts_dat_pct_np, ts_dat)
    return ts_dat_pct


def calc_change_helper(score_raw, short_win, long_win, ts_pct_win, sign=1, min_pct=0.9):
    score_change_raw = sign * (
            score_raw.rolling(short_win, int(min_pct * short_win)).mean() - score_raw.rolling(long_win, int(
        min_pct * long_win)).mean())
    score_change = calc_ts_pct(score_change_raw, ts_pct_win, min_pct=min_pct)
    return score_change


def calc_std_helper(score_raw, std_win, ts_pct_win, min_pct=0.9):
    score_std_raw = score_raw.rolling(std_win, int(min_pct * std_win)).std()
    score_std = calc_ts_pct(score_std_raw, ts_pct_win)
    return score_std


def calc_ma_helper(score_raw, ma_win, ts_pct_win, min_pct=0.9):
    score_ma_raw = score_raw.rolling(ma_win, int(min_pct * ma_win)).mean()
    score_ma = calc_ts_pct(score_ma_raw, ts_pct_win, min_pct=min_pct)
    return score_ma


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


class stk2indx_midret_amt_zsj_if(FactorGeneratorComplex):
    def __init__(self):
        super(stk2indx_midret_amt_zsj_if, self).__init__(
            required_columns=['close_hs300', 'amount_hs300', 'high_hs300', 'low_hs300', 'weight_boolean_hs300'],
            lookback_bars=2000)

    def on_bar(self, data):
        ## prep data
        stk_close = data['close_hs300']
        stk_high = data['high_hs300']
        stk_low = data['low_hs300']
        stk_amt = data['amount_hs300']
        bool_mask = data['weight_boolean_hs300']

        # factor logic
        # factor_name = 'stk2indx_midret_amt'
        roll_win_fac = 25
        min_pct = 0.9
        ma_win = 40
        ts_pct_win = 3000
        min_periods = int(min_pct * roll_win_fac)
        stk_mid = (stk_high + stk_low) / 2
        stk_mid_ret = stk_mid / stk_mid.shift(1) - 1
        stk_midret_amt_raw = stk_mid_ret * stk_amt
        stk_midret_amt_raw_ma = stk_midret_amt_raw.rolling(roll_win_fac, min_periods).mean()
        stk2indx_midret_amt_raw = stk_midret_amt_raw_ma[bool_mask].mean(axis=1)
        stk2indx_midret_amt = calc_ma_helper(stk2indx_midret_amt_raw, ma_win, ts_pct_win, min_pct)

        factor = stk2indx_midret_amt.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor<=-0.85] = 0
        # factor[factor>=0.5] = np.nan
        return factor

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


def delta(df1, d):
    # A_(i-d)
    output = df1.diff(periods=d)
    return output


def ts_median(df1, d):
    # time-series max over the past d periods.
    output = pd.DataFrame(bk.move_median(df1, window=d, min_count=int(d / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


class wsc_search6_long_if(FactorGenerator):
    def __init__(self):
        super(wsc_search6_long_if, self).__init__(required_columns=['open_spot'],
                                                  lookback_bars=2000)

    def on_bar(self, data):
        # 算法搜索
        data = data['open_spot'].to_frame()
        factor1 = delta(data, 20)
        factor = ts_median(factor1, 30)

        # factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = rolling_norm(factor, 600)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        factor[factor<=-0.5] = 0
        #factor[factor>=0.5] = np.nan
        return factor

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    return rolling_table


def reg_beta(df1, d):
    # 过去d期A对1:d回归的回归系数
    output = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
    for i in df1.columns:
        temp_y = df1[i].values
        temp_y = rolling_window(temp_y, d)
        temp_x = np.tile(np.arange(d) + 1, (temp_y.shape[0], 1))
        y = np.nansum((temp_y.T - np.nanmean(temp_y, axis=1).T) * (temp_x.T - np.nanmean(temp_x, axis=1).T), axis=0)
        x = np.nansum((temp_x.T - np.nanmean(temp_x, axis=1).T) ** 2, axis=0)
        flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
        flag = np.where(flag <= d - int(d / 2), 1, np.nan)
        output[i].iloc[d - 1:] = (y / x) * flag
    return output


def ts_delay(df1, d):
    # A_(i-d)
    output = df1.shift(periods=d)
    return output


def ts_mean(df1, d):
    # moving time-series average for the past d periods
    output = pd.DataFrame(bk.move_mean(df1, window=d, min_count=int(d / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


class wsc4_spot_kpz_if(FactorGenerator):
    def __init__(self):
        super(wsc4_spot_kpz_if, self).__init__(required_columns=['close_spot'],
                                                lookback_bars=2000)

    def on_bar(self, data):
        # dpo技术指标
        close = data['close_spot']
        N = 20
        dpo = close - ts_delay(ts_mean(close.to_frame(), N), int(N/2+1)).iloc[:,0]
        #factor = dpo
        # factor = rolling_norm(a, 240) + rolling_norm(b, 240)
        factor = abs(dpo - dpo.rolling(60, min_periods=30).median())#.rolling(10).mean()
        factor = factor.rolling(30, min_periods=10).mean()
        # factor = abs(factor - factor.rolling(500, min_periods=250).median())
        # print(factor)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = ts_rank(factor, 600*2)
        # factor[factor <= -0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 19:12:21 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator


class CloseVoltoMean_ICIF_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot']

        super(CloseVoltoMean_ICIF_CC_IF, self).__init__(
                                  required_columns=required_columns)
        


    def on_bar(self, data):

        prstd3_r = data['close_spot'].rolling(30, min_periods =10).std()/data['close_spot'].rolling(30, min_periods =15).mean()
        prstd3_r[abs(prstd3_r)>100000] = np.nan
        prstd3_r = prstd3_r.rolling(15, min_periods = 2).mean()
        factor = prstd3_r.to_frame()

        factor.columns =  [self.__class__.__name__]
        factor = ts_rank(factor)
        factor[factor>1] = 0
        factor[factor<=-0.5] = 0
        return factor


##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc14_cfg_ar_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc14_cfg_ar_if, self).__init__(required_columns=['close_hs300', 'weight_boolean_hs300', 'amount_hs300'],
                                             lookback_bars=3000)

    def on_bar(self, data):
        # mask
        bool_mask = data['weight_boolean_hs300']
        amount_mask = data['amount_hs300'][bool_mask]
        amount_rank_mask = 2 * amount_mask.rank(axis=1, pct=True) - 1

        # vidya技术指标,vi可用来衡量股票过去一段时间的趋势，趋势越强vi值越大，此时vidya赋予当前的close更大的权重，捕捉趋势，反之同理。
        stk_close = data['close_hs300']
        n = 10
        temp = ts_sum(abs(ts_delta(stk_close, 1)), n)
        temp[abs(temp)<1e-8] = np.nan
        vi = abs(ts_delta(stk_close, n)) / temp
        vidya = vi * stk_close + (1-vi) * ts_delay(stk_close, 1)
        factor_init = rolling_norm(vidya, 480)

        factor_raw = (factor_init * amount_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        factor = ts_rank(factor_mean, 240*12)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0] = 0
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk



class wyc_ts14_future_s_if(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_hs300'
        required_columns=['close' + suffix, 'weight_boolean' + suffix]
        lookback_bars=2000
        super(wyc_ts14_future_s_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        suffix = '_hs300'
        key = 'close' + suffix
        factor = pd.DataFrame(np.where(df[key] > delay(df[key], 2), std(df[key], 50), 0),
                              index=df[key].index, columns=df[key].columns)
        factor = ts_mean(factor, 30)

        factor = factor[df['weight_boolean' + suffix]]
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank_bk(factor, 5 * 242)
        factor.columns = [columnname]

        factor[factor < 0] = 0

        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc9_cfg_ar_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc9_cfg_ar_if, self).__init__(required_columns=['close_hs300', 'weight_boolean_hs300', 'amount_hs300', 'close_spot_if'],
                                             lookback_bars=2000)

    def on_bar(self, data):
        # mask
        bool_mask = data['weight_boolean_hs300']
        amount_mask = data['amount_hs300'][bool_mask]
        amount_rank_mask = 2 * amount_mask.rank(axis=1, pct=True) - 1

        # 比较股票和指数涨幅大小，大则置1，小则置0
        stk_close = data['close_hs300']
        index_close = data['close_spot_if']
        index_return = index_close.pct_change(3, fill_method=None)
        stk_return = stk_close.pct_change(3, fill_method=None)
        return_difference = stk_return.sub(index_return, axis=0)
        return_difference[return_difference > 0] = 1
        return_difference[return_difference <= 0] = 0
        temp = ts_sum(return_difference, 120)
        temp[abs(temp)<1e-8] = np.nan
        factor_init = ts_sum(return_difference, 20) / temp
        factor_init = factor_init.replace([-np.inf, np.inf], np.nan)

        factor_raw = (factor_init * amount_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 45)
        factor = ts_rank(factor_mean, 240*5)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        factor[factor>=0] = 0
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 15:45:21 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class ClMaxClMin_ind_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot_if']
 
        super(ClMaxClMin_ind_CC_IF, self).__init__(
                                  required_columns=required_columns)
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def on_bar(self, data):
        m_vwap_ind_r = (data['close_spot_if']).rolling(60, min_periods = 30).max()/data['close_spot_if'].rolling(60, min_periods = 30).min()
        factor = m_vwap_ind_r.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        return factor


##########
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 11:00:21 2021

@author: appadmin
"""
import pandas as pd
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *
import numpy as np

class CFG7_2_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['open_hs300', 'weight_boolean_hs300','weight_hs300', 'close_hs300', 'turnover_hs300', 'weight_boolean_hs300']

        super(CFG7_2_CC_IF, self).__init__(required_columns=required_columns
                                  )
        
    def on_bar(self, df):
        columnname = self.__class__.__name__
        to = df['turnover_hs300']
        hclose = df['close_hs300']
        
        hopen = df['open_hs300']
        
        df_s = df['weight_hs300']#.rolling(120, min_periods = 15).sum()
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0)

        ret = hclose/hopen -1
        hret = hclose/hclose.shift(1) -1
        ret = ret.replace([np.inf, -np.inf], np.nan)
        hret = hret.replace([np.inf, -np.inf], np.nan)
        cc1 = ((to[hclose<hopen]/abs(ret[hclose<hopen])))
        cc1[abs(cc1) > 100000] = np.nan
        ccc1 = cc1.rolling(90, min_periods = 7).mean()
        ccc1 = ccc1[bool_df]
        hret = hret[bool_df]
        cc2 = to_ts(ccc1, hret)
        ccc2 = cc2.rolling(90, min_periods = 15).mean()
        cc3 = rolling_norm(ccc2.to_frame(), method = 'ts_rank')
        #cc3 = cc3.rolling(3, min_periods = 2).mean()
        cc3[cc3<=-1] = np.nan
        cc3[cc3>1] = np.nan
        cc3.columns = [columnname]
        return cc3
##########
from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np

class xdy_ts1_spot_if(FactorGenerator):
    def __init__(self):
        required_columns=['high_spot_if', 'close_spot_if']
        lookback_bars=2000
        super(xdy_ts1_spot_if, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        high = df['high_spot_if']
        close = df['close_spot_if']
        high[abs(high) < 1e-8] = np.nan
        gain_high_60 = high / high.shift(30) - 1
        h_c = close / high - 1
        a = mean(h_c, 60)
        a[abs(a) < 1e-8] = np.nan
        factor = ts_sum(gain_high_60 / a, 10)
        factor = mean(factor, 10) * -1
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_norm(factor, 5 * 242)
        factor.loc[factor[columnname] <= -0.5] = 0

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:38:46 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class LminLmean_ICIF_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns =['low', 'recent_month_mask']
        super(LminLmean_ICIF_CC_IF, self).__init__(
                                  required_columns=required_columns)
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa

    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa
    
    def on_bar(self, data):

        ctl_r = -data['low'].rolling(60, min_periods =15).min()/data['low'].rolling(15, min_periods =5).mean()
        factor = ctl_r[data['recent_month_mask']].mean(axis = 1).to_frame()

        factor.columns = [self.__class__.__name__]
        factor = self.normalization(factor, 242*2)
        factor = factor.rolling(5, min_periods = 3).mean()
        factor = self.normalization(factor, 242*2)
        factor = self.normalization(factor, 242*2)
        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts6_spot_if(FactorGenerator):
    def __init__(self):
        required_columns=['volume_spot_if','high_spot_if','low_spot_if','close_spot_if']
        lookback_bars=2000
        super(wyc_ts6_spot_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        N = 20
        a = (df['high_spot_if'] - df['low_spot_if'])
        a[abs(a) < 1e-8] = np.nan
        factor = sma(df['volume_spot_if'] * (
                    (df['close_spot_if'] - df['low_spot_if']) - (df['high_spot_if'] - df['close_spot_if'])) / a, N, 1)
        factor = ts_rank_bk(factor, 240)
        factor = ts_mean(factor, 20)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        return factor

##########
from factor_generator import FactorGenerator
from operators_wsc import *
from help_functions_wsc import multi_processing_joblib



class wsc_gp3_spot_if(FactorGenerator):
    def __init__(self):
        super().__init__(required_columns=['low_spot_if'], lookback_bars=2000)

    def on_bar(self, data_dict):
        # gp搜索因子，搜索时间段：20170101-20181231，验证时间段：20190101-20190630
        # low的收益率作差后取中位数，收益率涨幅越大因子值越大，属于动量因子。
        index_low = data_dict['low_spot_if']
        factor_raw = ts_median(ts_delta(ts_pct_change(index_low, 120), 115), 25)
        factor = ts_rank(factor_raw, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts4_icspot_if(FactorGenerator):
    def __init__(self):
        required_columns=['close_spot']
        lookback_bars=2000
        super(wyc_ts4_icspot_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):

        N = 100
        factor = pd.DataFrame(np.where((delta((ts_sum(df['close_spot'], N) / N), N) / delay(df['close_spot'], N))<=0.05,(-1 * (df['close_spot'] - ts_min(df['close_spot'], N))),(-1 * delta(df['close_spot'], 3))),index=df['close_spot'].to_frame().index,columns=df['close_spot'].to_frame().columns)
        factor = ts_mean(ts_rank(-1*factor, 100),N)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_norm(factor, 5 * 242)
        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np

class wyc_ts14_icspot_if(FactorGenerator):
    def __init__(self):
        required_columns=['close_spot']
        lookback_bars=2000
        super(wyc_ts14_icspot_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        factor = pd.DataFrame(np.where(df['close_spot'] > delay(df['close_spot'], 1), std(df['close_spot'], 50), 0),
                              index=df['close_spot'].to_frame().index, columns=df['close_spot'].to_frame().columns)
        factor = ts_rank_bk(factor, 60)
        factor = ts_mean(factor, 30)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        factor[factor <= -0.5] = 0
        return factor
##########
from factor_generator import FactorGenerator
from operators_wsc import *
from help_functions_wsc import multi_processing_joblib



class wsc_gp1_future_if(FactorGenerator):
    def __init__(self):
        super(wsc_gp1_future_if, self).__init__(required_columns=['low_if' ,'amount_if', 'position_if', 'recent_month_mask'],
                                                lookback_bars=2000)

    def on_bar(self, data_dict):
        # gp搜索因子，搜索时间段：20170101-20180831，验证时间段：20180901-20181231
        # 因子逻辑：第一部分是low在最近一段时间的位置，属于动量；第二部分是amount和position的相关系数，两者都很大可能是持仓和交易额齐飞，看涨，两者都很小可能是反弹的预兆，看涨，如果这个逻辑也能成立的话这部分也是动量。
        # 测了一下，两部分分别作为单因子表现也都还可以，尤其是前者，可以作为单因子入库，但是都不如叠加之后表现好。
        future_low = data_dict['low_if']
        future_amount = data_dict['amount_if']
        future_position = data_dict['position_if']
        future_mask = data_dict['recent_month_mask']
        factor_raw = max2(rolling_norm(future_low, 115)[future_mask].sum(axis=1), ts_corr(future_amount, future_position, 90)[future_mask].sum(axis=1))
        factor = ts_rank(factor_raw, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
author:       sujian zhi
fred:         minute
prod:         IC.CFE
factor_name:  fac
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
from utils_zsj import *

"""
import inspect, os, sys
code_base = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.dirname(code_base))
from ts.factor.minute.utils_zsj import *
"""


class retvol_zsj_if(FactorGenerator):
    def __init__(self):
        super(retvol_zsj_if, self).__init__(required_columns=['close_if', 'recent_month_mask'],
                                            lookback_bars=400)

    def on_bar(self, data):
        ##### def data #####
        mask = data['recent_month_mask']
        close = data['close_if']
        minute_ret = close / close.shift(5) - 1

        ##### calc factor #####
        """retvol"""
        vol_win = 60
        ts_pct_win = 240
        retvol_raw = minute_ret.rolling(vol_win, 1).std()
        retvol = calc_ts_pct(retvol_raw, ts_pct_win)
        retvol = retvol[mask].sum(axis=1)

        ##### format factor #####
        retvol.name = self.__class__.__name__
        factor = pd.DataFrame(retvol)
        factor[factor <= -0.5] = 0
        return factor

##########
from factor_generator import FactorGenerator
import pandas as pd
import numpy as np
import bottleneck as bk


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

class rt1_zf_if(FactorGenerator):
    def __init__(self):
        required_columns = ['close_spot_if', 'low_spot_if']
        super(rt1_zf_if, self).__init__(required_columns=required_columns)

    def on_bar(self, data):
        lowdf = data['low_spot_if']
        lowdf[abs(lowdf) < 1e-8] = np.nan
        sig = data['close_spot_if'] / data['low_spot_if'].rolling(60, min_periods=30).min()
        sig = ts_rank(sig, 242 * 2)
        sig = sig.rolling(10, min_periods=2).mean()
        sig[sig <= -0.5] = 0
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)

##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts20_icspot_if(FactorGenerator):
    def __init__(self):

        required_columns=['close_spot','low_spot','high_spot','volume_spot']
        lookback_bars=2000
        super(wyc_ts20_icspot_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        a = (df['high_spot'] - df['low_spot'])
        a[abs(a) < 1e-8] = np.nan
        factor = ts_sum(((df['close_spot'] - df['low_spot']) - (df['high_spot'] - df['close_spot'])) / a * df['volume_spot'], 20)
        # factor = ts_mean(factor, 5)
        factor = ts_rank(factor, 4 * 242)
        factor = ts_mean(factor, 20)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 4 * 242)
        return factor
##########
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np
from functools import partial


def place_back_format(dat_mat, dat_orig):
    if isinstance(dat_orig, pd.DataFrame):
        dat_fmt = pd.DataFrame(dat_mat, index=dat_orig.index, columns=dat_orig.columns)
    elif isinstance(dat_orig, pd.Series):
        dat_fmt = pd.Series(dat_mat, index=dat_orig.index)
        dat_fmt.name = dat_orig.name
    else:
        dat_fmt = dat_mat
    return dat_fmt


def calc_ts_pct(ts_dat, roll_win=20, min_pct=1, force_range=False):
    min_win = int(min_pct * roll_win)
    ts_dat_pct_np = bk.move_rank(ts_dat, window=roll_win, min_count=min_win, axis=0)
    if force_range:
        ts_dat_pct_np = (ts_dat_pct_np + 1) / 2
    ts_dat_pct = place_back_format(ts_dat_pct_np, ts_dat)
    return ts_dat_pct


def calc_change_helper(score_raw, short_win, long_win, ts_pct_win, sign=1, min_pct=0.9):
    score_change_raw = sign * (
            score_raw.rolling(short_win, int(min_pct * short_win)).mean() - score_raw.rolling(long_win, int(
        min_pct * long_win)).mean())
    score_change = calc_ts_pct(score_change_raw, ts_pct_win, min_pct=min_pct)
    return score_change


def calc_std_helper(score_raw, std_win, ts_pct_win, min_pct=0.9):
    score_std_raw = score_raw.rolling(std_win, int(min_pct * std_win)).std()
    score_std = calc_ts_pct(score_std_raw, ts_pct_win)
    return score_std


def calc_ma_helper(score_raw, ma_win, ts_pct_win, min_pct=0.9):
    score_ma_raw = score_raw.rolling(ma_win, int(min_pct * ma_win)).mean()
    score_ma = calc_ts_pct(score_ma_raw, ts_pct_win, min_pct=min_pct)
    return score_ma


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


class stk2idx_ret_ch_corr_zsj_if(FactorGeneratorComplex):
    def __init__(self):
        super(stk2idx_ret_ch_corr_zsj_if, self).__init__(required_columns=['close_hs300', 'amount_hs300', 'high_hs300', 'weight_boolean_hs300'],
                                                         lookback_bars=2000)

    def on_bar(self, data):
        ## prep data
        stk_close = data['close_hs300']
        stk_amt = data['amount_hs300']
        bool_mask = data['weight_boolean_hs300']

        # factor logic
        stk_high = data['high_hs300']
        stk_ret_close = stk_close/stk_close.shift(1) - 1
        stk_ret_high = stk_high/stk_high.shift(1) - 1
        ret_close_high_corr_raw = stk_ret_close[bool_mask].corrwith(stk_ret_high[bool_mask],axis=1)
        ma_win = 45
        ts_pct_win = 1200
        min_pct = 0.9
        stk2idx_ret_ch_corr = calc_ma_helper(ret_close_high_corr_raw,ma_win,ts_pct_win,min_pct)
        factor = stk2idx_ret_ch_corr.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts39_icfuture_if(FactorGenerator):
    def __init__(self):

        required_columns=['close', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts39_icfuture_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        factor = multi_processing_joblib(df=df['close'] - delay(df['close'], 20), func=ts_truncated_ema, n_jobs=-1, d=200, alpha= 1/30)

        factor = ts_mean(factor, 10)
        mask = df['recent_month_mask']
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor[factor <= -0.5] = 0

        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc5_cfg_ar_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc5_cfg_ar_if, self).__init__(required_columns=['close_hs300', 'weight_boolean_hs300', 'amount_hs300'],
                                             lookback_bars=2000)

    def on_bar(self, data):
        # mask
        bool_mask = data['weight_boolean_hs300']
        amount_mask = data['amount_hs300'][bool_mask]
        amount_rank_mask = 2 * amount_mask.rank(axis=1, pct=True) - 1

        # 计算长短两条均线包围的面积
        stk_close = data['close_hs300']
        ma_long = ts_mean(stk_close, 90)
        ma_short = ts_mean(stk_close, 15)
        ma_diff = ma_short - ma_long
        factor_init = ma_diff
        factor_raw = (factor_init * amount_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 10)
        factor = ts_rank(factor_mean, 240)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 14:54:10 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator


class HL123_ICIF_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns=['low', 'high', 'recent_month_mask']

        super(HL123_ICIF_CC_IF, self).__init__(required_columns=required_columns)
    

    

    
    def on_bar(self, df):
        columnname = self.__class__.__name__
        hlow = df['low']
        hhigh = df['high']
        i11 = hhigh.rolling(10, min_periods = 5).max()-hlow.rolling(60, min_periods = 10).min()
        i12 = (hhigh.shift(30)).rolling(10, min_periods = 5).max()-(hlow.shift(30)).rolling(60, min_periods = 10).min()
        i2 = (i11-i12).rolling(20, min_periods = 2).mean()
        i2 = ts_rank(i2[df['recent_month_mask']].mean(axis = 1).to_frame())

        i2[i2<=-0.5] = 0
        i2.columns = [columnname]    
        return i2
##########
from factor_generator import FactorGenerator
from operators_wyc import *

class wyc_ts38_icspot_if(FactorGenerator):
    def __init__(self):

        required_columns=['close_spot']
        lookback_bars=2000
        super(wyc_ts38_icspot_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        smaM = 50
        stdN = 10
        temp1 = df['close_spot'].copy()
        temp1[df['close_spot'] > delay(df['close_spot'], 1)] = std(df['close_spot'], stdN)
        temp1[df['close_spot'] <= delay(df['close_spot'], 1)] = 0
        a = ts_truncated_ema(temp1, 5 * 242, 1/smaM)
        temp1[df['close_spot'] > delay(df['close_spot'], 1)] = 0
        temp1[df['close_spot'] <= delay(df['close_spot'], 1)] = std(df['close_spot'], stdN)
        b = ts_truncated_ema(temp1, 5 * 242, 1/smaM)
        c = a + b
        c[abs(c) < 1e-8] = np.nan
        factor = a / c * 100
        factor = ts_rank(factor, 120)
        factor = ts_mean(factor, 20)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_norm(factor, 5 * 242)

        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np


class xdy_ts6_spot_if(FactorGenerator):
    def __init__(self):
        required_columns = ['close_spot_if']
        lookback_bars = 2000
        super(xdy_ts6_spot_if, self).__init__(required_columns=required_columns,
                                              lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        close = df['close_spot_if']
        gain_close_30 = ts_gain(close, 15)
        factor = ts_levelchange(gain_close_30, 20)
        factor = mean(factor, 150)
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_norm(factor, 5 * 242)
        # factor.loc[factor[columnname] <= -0.3] = np.nan

        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 10:16:36 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex

class cd_ind_vl_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_boolean_hs300', 'close_hs300']

        super(cd_ind_vl_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa
    
    def ts_std(self, df1, d):
        # moving time-series rank for the past d periods
        if isinstance(df1, pd.DataFrame):
            output = pd.DataFrame(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                                  index=df1.index, columns=df1.columns)
        elif isinstance(df1, pd.Series):
            output = pd.Series(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                               index=df1.index, name=df1.name)
        return output
    
    def on_bar(self, data):
        stk_close = data['close_hs300']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = self.ts_std(stk_ret, 30)
        stk_volatility = stk_volatility[data['weight_boolean_hs300']]
        mask = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.90, axis = 1)), axis=0)
        temp = data['close_hs300'].rolling(65, min_periods = 2).mean().diff()
        tempdf = (temp*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(5, min_periods = 5).mean()
        factor = self.ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np


class xdy_ts4_spot_if(FactorGenerator):
    def __init__(self):
        required_columns = ['high_spot_if']
        lookback_bars = 2000
        super(xdy_ts4_spot_if, self).__init__(required_columns=required_columns,
                                              lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        high = df['high_spot_if']
        factor = ts_position(high, 30)
        factor = -1 * factor.rolling(75, min_periods=20).skew()
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_norm(factor, 5 * 242)
        # factor.loc[factor[columnname] <= -0.5] = np.nan

        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk

class wyc_ts5_future_nr_tr_if(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_hs300'
        required_columns=['volume' + suffix,'high' + suffix,'close' + suffix,'amount' + suffix,'turnover' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(wyc_ts5_future_nr_tr_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_hs300'
        columnname = self.__class__.__name__

        N = 45
        factor = pd.DataFrame(np.where((delta((ts_sum(df['close' + suffix], N) / N), N) / delay(df['close' + suffix], N))<=0.05,(-1 * (df['close' + suffix] - ts_min(df['close' + suffix], N))),(-1 * delta(df['close' + suffix], 3))),index=df['close' + suffix].index,columns=df['close' + suffix].columns)
        factor = ts_mean(ts_rank(-1*factor, 1200),15)

        factor = rolling_norm(factor, 5 * 242)

        t = df['turnover' + suffix][df['weight_boolean' + suffix]]
        tr = (2 * t.rank(axis=1, pct=True) - 1)
        factor = factor * tr
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 300)
        factor = ts_mean(factor, 15)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]
        factor[factor < 0] = 0


        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 14:16:19 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator


class LMLS_ind_ICIF_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns=['low', 'recent_month_mask']

        super(LMLS_ind_ICIF_CC_IF, self).__init__(required_columns=required_columns)
    

    

    def on_bar(self, data):

        temp = data['low'].rolling(75, min_periods = 15).mean() - data['low'].shift(30).rolling(45, min_periods = 7).mean()
        factor = temp[data['recent_month_mask']].mean(axis = 1).to_frame()
        factor = ts_rank(factor)
        factor[factor<-0.5] = 0
        factor.columns = [self.__class__.__name__]
        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np

class wyc_ts34_icfuture_if(FactorGenerator):
    def __init__(self):

        required_columns=['close','high','low','volume', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts34_icfuture_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        a = (df['high'] - df['low'])
        a[abs(a) < 1e-8] = np.nan
        factor = ((df['close'] - df['low']) - (df['high'] - df['close'])) / a * df['volume']
        factor = ts_mean(factor, 150)
        mask = df['recent_month_mask']
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor[factor <= -0.5] = 0

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 11:09:22 2021

@author: appadmin
"""
import pandas as pd
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *
import numpy as np

class CFG8_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_boolean_hs300','volume_hs300', 'close_hs300', 'float_shares_hs300']

        super(CFG8_CC_IF, self).__init__(required_columns=required_columns
                                  )
        
    def on_bar(self, df):
        columnname = self.__class__.__name__
        hvolume = df['volume_hs300']
        hclose = df['close_hs300']
        hfs = df['float_shares_hs300']
        hret = hclose/hclose.shift(1) - 1
        d1 = hvolume/hclose/hfs
        
        hret = hret.replace([-np.inf, np.inf], np.nan)
        d1 = d1.replace([-np.inf, np.inf], np.nan)
        
        d1 = d1[df['weight_boolean_hs300']]
        hret = hret[df['weight_boolean_hs300']]
        d1 = to_ts(d1, hret)
        dd1 = d1.rolling(45, min_periods = 15).mean()
        dd2 = rolling_norm(dd1.to_frame())
        dd2.columns = [columnname]
        dd2[dd2<=-0.5] = 0
        dd2[dd2>1] = np.nan
        
        return dd2

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 15:44:39 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator
import talib.abstract as ta


class SLCS_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot_if']

        super(SLCS_CC_IF, self).__init__(
                                  required_columns=required_columns)
        

    


    
    def on_bar(self, data):


        close_spot = data['close_spot_if'].values
        
        ind = list(range(len(close_spot)))

        m_vwap_ind_r = rolling_linear_reg(ind, close_spot, 60)
        #factor = pd.Series(data['close_spot_if'].rolling(25, min_periods = 1).skew()).to_frame()
        factor = pd.Series(m_vwap_ind_r).to_frame()
        factor.index = data['close_spot_if'].index
        factor.columns = [self.__class__.__name__]

        factor = ts_rank(factor)
        factor[factor<=-0.5] = np.nan
        factor = ts_rank(factor, 242*4)
        factor[factor<=-0.5] = 0
        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts28_future_if(FactorGenerator):
    def __init__(self):

        required_columns=['close_if', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts28_future_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        mask = df['recent_month_mask']
        M = 40
        con1 = df['close_if'] > delay(df['close_if'], 20)
        factor = ts_sum(con1, M) / M * 100
        factor = ts_mean(factor, 30)
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        factor = factor[mask].sum(axis=1).to_frame()

        factor.columns = [columnname]
        factor[factor <= -0.2] = 0
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 11:05:26 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator

def normalization(signal, holding_window = 1200): 
    max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
    min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
    a = (signal - min_s)/(max_s-min_s)
    a = 2*a-1
    aa = pd.DataFrame(a)
    aa.index = signal.index
    aa.columns = signal.columns
    return aa

class VwLs_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['vwap_if', 'recent_month_mask']

        super(VwLs_CC_IF, self).__init__(
                                  required_columns=required_columns
                                  )

    def on_bar(self, data):

        price_diff_1 = data['vwap_if']/data['vwap_if'].shift(1)-1
        price_diff_30 = data['vwap_if']/data['vwap_if'].shift(60)-1
        copcor1_r = -(price_diff_1-price_diff_30).rolling(15, min_periods = 5).mean()       
        factor = copcor1_r[data['recent_month_mask']].mean(axis = 1).to_frame()

        factor.columns = [self.__class__.__name__]
        factor = normalization(factor, 2420)
        factor[factor>1] = 0
        factor[factor<=-0.5] = 0
        return factor


##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc14_cfg_cr_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc14_cfg_cr_if, self).__init__(required_columns=['close_hs300', 'stk_index_corr_hs300'],
                                              lookback_bars=2000)

    def on_bar(self, data):
        # mask
        corr_mask = data['stk_index_corr_hs300']
        corr_rank_mask = 2 * corr_mask.rank(axis=1, pct=True) - 1

        # vidya技术指标,vi可用来衡量股票过去一段时间的趋势，趋势越强vi值越大，此时vidya赋予当前的close更大的权重，捕捉趋势，反之同理。
        stk_close = data['close_hs300']
        n = 10
        temp = ts_sum(abs(ts_delta(stk_close, 1)), n)
        temp[abs(temp)<1e-8] = np.nan
        vi = abs(ts_delta(stk_close, n)) / temp
        vidya = vi * stk_close + (1-vi) * ts_delay(stk_close, 1)
        factor_init = rolling_norm(vidya, 90)

        factor_raw = (factor_init * corr_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        factor = ts_rank(factor_mean, 240*8)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc8_cfg_ws_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc8_cfg_ws_if, self).__init__(required_columns=['close_hs300', 'weight_hs300', 'volume_hs300'],
                                             lookback_bars=3000)

    def on_bar(self, data):
        #mask
        stk_weight = data['weight_hs300']

        # close和volume的价量背离
        stk_close = data['close_hs300']
        stk_volume = data['volume_hs300']
        factor_init = stk_close.rolling(45, min_periods=15).cov(stk_volume)
        factor_raw = (factor_init * stk_weight).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 10)
        factor = ts_rank(factor_mean, 240*8)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 17:44:46 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np
from factor_generator import FactorGenerator

# demo
class HLDL2_ind_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['high_spot_if', 'low_spot_if']

        super(HLDL2_ind_CC_IF, self).__init__(
                                  required_columns=required_columns)



    def on_bar(self, data):


        t_pcorr = (data['high_spot_if'].diff()+data['low_spot_if'].diff()).rolling(90, min_periods = 45).mean()
        factor = t_pcorr.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = rolling_norm(factor)
        factor[factor<0] = 0
        return factor

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    return rolling_table


def reg_beta(df1, d):
    # 过去d期A对1:d回归的回归系数
    output = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
    for i in df1.columns:
        temp_y = df1[i].values
        temp_y = rolling_window(temp_y, d)
        temp_x = np.tile(np.arange(d) + 1, (temp_y.shape[0], 1))
        y = np.nansum((temp_y.T - np.nanmean(temp_y, axis=1).T) * (temp_x.T - np.nanmean(temp_x, axis=1).T), axis=0)
        x = np.nansum((temp_x.T - np.nanmean(temp_x, axis=1).T) ** 2, axis=0)
        flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
        flag = np.where(flag <= d - int(d / 2), 1, np.nan)
        output[i].iloc[d - 1:] = (y / x) * flag
    return output


class wsc_mean_plus_std2_if(FactorGenerator):
    def __init__(self):
        super(wsc_mean_plus_std2_if, self).__init__(required_columns=['close_spot_if'],
                                                   lookback_bars=2000)

    def on_bar(self, data):
        # 计算过去5分钟收益率的均值和标准差的线性组合
        a = data['close_spot_if'].pct_change(5)
        b = a.rolling(30, min_periods=15).mean()
        c = a.rolling(30, min_periods=15).std()
        factor = 1.5 * b + c
        factor = factor.rolling(10).mean()
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = ts_rank(factor, 1200)
        # factor[factor <= -0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import numpy as np

class xdy_ts2_spot_tr_if(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_hs300'
        required_columns=['high' + suffix, 'low' + suffix,'turnover' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(xdy_ts2_spot_tr_if, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_hs300'
        columnname = self.__class__.__name__

        high = df['high' + suffix]
        low = df['low' + suffix]
        gain_high_20 = high / high.shift(20) - 1
        factor = (low * gain_high_20).ewm(25).mean()

        t = df['turnover' + suffix][df['weight_boolean' + suffix]]
        tr = (2 * t.rank(axis=1, pct=True) - 1)
        factor = factor * tr
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank_bk(factor, 300)
        factor = ts_mean(factor, 10)
        factor = ts_rank_bk(factor, 5 * 242)
        factor.columns = [columnname]

        factor[factor > 0] = 0

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 17:19:45 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator
# demo
class GA_ind_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot_if', 'low_spot_if', 'open_spot_if', 'high_spot_if']

        super(GA_ind_CC_IF, self).__init__(
                                  required_columns=required_columns)

    

    def on_bar(self, data):

        n = 120
        a = data['high_spot_if'].rolling(n, min_periods = int(n/2)).max()-data['open_spot_if'].shift(n)
        b = data['close_spot_if'] - data['low_spot_if'].rolling(n, min_periods = int(n/2)).min()
        c = (data['high_spot_if'].rolling(n, min_periods = int(n/2)).max()-data['low_spot_if'].rolling(n, min_periods = int(n/2)).min())*2
        
        vwtc_r = (a*b)/c
        vwtc_r = vwtc_r.replace([-np.inf, np.inf], np.nan)
        factor = vwtc_r.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor, 242*3)
        factor[factor<=-0.5] = 0
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
author:       sujian zhi
fred:         minute
prod:         IC.CFE
factor_name:  fac
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
from utils_zsj import *

"""
import inspect, os, sys
code_base = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.dirname(code_base))
from ts.factor.minute.utils_zsj import *
"""


class vwap_ma_zsj_if(FactorGenerator):
    def __init__(self):
        super(vwap_ma_zsj_if, self).__init__(required_columns=['close_if', 'high_if', 'low_if', 'volume_if', 'recent_month_mask'],
                                             lookback_bars=1300)

    def on_bar(self, data):
        ##### def data #####
        close = data['close_if']
        high = data['high_if']
        low = data['low_if']
        volume = data['volume_if']
        mask = data['recent_month_mask']

        ##### calc factor #####
        def calc_vwap_sig(close, high, low, volume, roll_win):
            typical = (high + low + close) / 3
            mf = volume * typical
            volume_sum = SUM(volume, roll_win)
            volume_sum[abs(volume_sum) < 1e-8] = np.nan
            mf_sum = SUM(mf, roll_win)
            vwap_val = mf_sum / volume_sum
            vwap_diff = close - vwap_val
            return vwap_diff

        """vwap_ma"""
        factor_name = 'vwap_ma'
        roll_win = 10
        ma_win = 45
        ts_pct_win = 1500
        score_raw = calc_vwap_sig(close, high, low, volume, roll_win)
        vwap_ma = calc_ma_helper(score_raw, ma_win, ts_pct_win)
        vwap_ma = vwap_ma[mask].sum(axis=1)

        ##### format factor #####
        vwap_ma.name = self.__class__.__name__
        factor = pd.DataFrame(vwap_ma)
        factor[factor<=-0.5]=0
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc21_cfg_vs_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc21_cfg_vs_if, self).__init__(required_columns=['close_hs300', 'high_hs300', 'low_hs300', 'open_hs300', 'stk_volatility_hs300'],
                                              lookback_bars=2000)

    def on_bar(self, data):
        # mask
        volatility_mask = data['stk_volatility_hs300']

        # 根据asi指标改造而来
        # asi指标由si累加而来，但这样会导致每个时刻累加的起点不同，因此用si过去一段时间的移动平均代替，解决起点不同的问题
        stk_close = data['close_hs300']
        stk_high = data['high_hs300']
        stk_low = data['low_hs300']
        stk_open = data['open_hs300']
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
        r4 = r2.copy(deep=True)
        r4[(a>=b)&(a>=c)] = r1
        r = r4.copy(deep=True)
        r[(c>=a)&(c>=b)] = r3
        r[abs(r)<1e-8] = np.nan
        m[abs(m)<1e-8] = np.nan
        si = 50 * (ts_delta(stk_close, 1) + ts_delay(stk_close, 1) - ts_delay(stk_open, 1) + 0.5*(stk_close - stk_open)) / r * k / m
        factor_init = si

        factor_raw = (factor_init * volatility_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 60)  # 45
        factor = ts_rank(factor_mean, 240*5)  # 240*3
        
        factor = factor.to_frame() 
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor <= 0] = 0
        #factor[factor>=0.5] = np.nan
        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk


class wyc_ts34_future_nr_as_if(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_hs300'
        required_columns=['close' + suffix,'high' + suffix,'low' + suffix,'volume' + suffix,'amount' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(wyc_ts34_future_nr_as_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_hs300'
        columnname = self.__class__.__name__
        hl = (df['high' + suffix]-df['low' + suffix])
        hl[abs(hl) < 1e-8] = np.nan    
        factor = ((df['close' + suffix]-df['low' + suffix])-(df['high' + suffix]-df['close' + suffix]))/hl*df['volume' + suffix]
        factor = ts_mean(factor, 150)

        factor = rolling_norm(factor, 5 * 242)

        a = df['amount' + suffix][df['weight_boolean' + suffix]]
        factor = factor * a
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 150)
        factor = ts_mean(factor, 15)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        factor[factor < 0] = 0

        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np


class wyc_ts49_future_if(FactorGenerator):
    def __init__(self):
        required_columns = ['close_if', 'recent_month_mask']
        lookback_bars = 2000
        super(wyc_ts49_future_if, self).__init__(
            required_columns=required_columns,
            lookback_bars=lookback_bars)

    def on_bar(self, df):
        con1 = ((delta((ts_sum(df['close_if'], 100) / 100), 100) / delay(df['close_if'], 100)) <= 0.05)
        temp1 = df['close_if'].copy(deep=True)
        temp1[con1] = (df['close_if'] - ts_min(df['close_if'], 200))
        temp1[~con1] = delta(df['close_if'], 10)
        factor = temp1
        factor = ts_rank(factor, 75)
        factor = mean(factor, 30)
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 5 * 242)
        mask = df['recent_month_mask']
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 08:45:14 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex

class hhll_t3_CC_CFG_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['turnover_hs300', 'weight_boolean_hs300', 'close_hs300', 'high_hs300', 'low_hs300']

        super(hhll_t3_CC_CFG_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, df):
        turnover = (df['turnover_hs300'].rolling(60, min_periods = 15).mean())[df['weight_boolean_hs300']]
        ret = (df['close_hs300']/df['close_hs300'].shift(30)-1)[df['weight_boolean_hs300']]
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)
        temp6 = ret.gt(pd.Series(ret.quantile(0.80, axis = 1)), axis=0)
        mask = temp4*temp6
        temp1 = (df['high_hs300']>df['high_hs300'].shift(1)).astype(int)
        temp2 = (df['low_hs300']>df['low_hs300'].shift(1)).astype(int)
        
        temp =  temp1+temp2
        temp[temp==2] = 4
        tempdf = (temp*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(60, min_periods = 2).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk

class wyc_ts6_future_ws_if(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_hs300'
        required_columns=['volume' + suffix,'high' + suffix,'low' + suffix,'close' + suffix,'weight' + suffix]
        lookback_bars=2000
        super(wyc_ts6_future_ws_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_hs300'
        columnname = self.__class__.__name__

        N = 45
        a = (df['high' + suffix] - df['low' + suffix])
        a[abs(a) < 1e-8] = np.nan
        factor = df['volume'+ suffix] * ((df['close' + suffix] - df['low' + suffix]) - (df['high' + suffix] - df['close' + suffix])) / a
        factor = multi_processing_joblib(df=factor, func=ts_truncated_ema, n_jobs=-1, d=200, alpha= 1/N)
        factor = ts_rank(factor, 1200)
        factor = ts_mean(factor, 15)

        factor = factor * df['weight' + suffix]
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 150)
        factor = ts_mean(factor, 10)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]
        factor[factor > 0] = 0

        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc9_cfg_ws_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc9_cfg_ws_if, self).__init__(required_columns=['close_hs300', 'close_spot_if', 'weight_hs300'],
                                             lookback_bars=2000)

    def on_bar(self, data):
        #mask
        stk_weight = data['weight_hs300']

        # 比较股票和指数涨幅大小，大则置1，小则置0
        stk_close = data['close_hs300']
        index_close = data['close_spot_if']
        index_return = index_close.pct_change(3, fill_method=None)
        stk_return = stk_close.pct_change(3, fill_method=None)
        return_difference = stk_return.sub(index_return, axis=0)
        return_difference[return_difference > 0] = 1
        return_difference[return_difference <= 0] = 0
        temp = ts_sum(return_difference, 120)
        temp[abs(temp)<1e-8] = np.nan
        factor_init = ts_sum(return_difference, 20) / temp
        factor_init = factor_init.replace([-np.inf, np.inf], np.nan)

        factor_raw = (factor_init * stk_weight).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 45)
        factor = ts_rank(factor_mean, 240*2)
        factor = -1 * factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np

class wyc_ts14_spot_if(FactorGenerator):
    def __init__(self):
        required_columns=['close_spot_if']
        lookback_bars=2000
        super(wyc_ts14_spot_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        factor = pd.DataFrame(
            np.where(df['close_spot_if'] > delay(df['close_spot_if'], 1), std(df['close_spot_if'], 50), 0),
            index=df['close_spot_if'].to_frame().index, columns=df['close_spot_if'].to_frame().columns)
        factor = ts_rank(factor, 60)
        factor = ts_mean(factor, 40)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 5 * 242)
        factor[factor <= -0.5] = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 13:07:56 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex

class HHLS_ar_CC_CFG_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_boolean_hs300',  'high_hs300', 'amount_hs300']

        super(HHLS_ar_CC_CFG_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, data):

        stk_amount = (data['amount_hs300'])[data['weight_boolean_hs300']]
        
        stk_amount_rank = 2 * stk_amount.rank(axis=1, pct=True) - 1
        mask = stk_amount_rank
        temp = data['high_hs300'].rolling(50, min_periods = 15).max() - data['high_hs300'].shift(50).rolling(50, min_periods = 7).max()
        tempdf = (temp*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(5, min_periods = 3).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor
##########
from factor_generator import FactorGenerator
import pandas as pd
import numpy as np
import bottleneck as bk

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

class sr1_zf_if(FactorGenerator):
    def __init__(self):
        required_columns = ['close_spot_if', 'low_spot_if']
        super(sr1_zf_if, self).__init__(required_columns=required_columns)

    def on_bar(self, data):
        rtn = data['close_spot_if'] / data['close_spot_if'].shift(1) - 1
        vol = rtn.rolling(60, min_periods=30).std()
        vol[vol < 1e-8] = np.nan
        ret = data['close_spot_if'] / (data['low_spot_if'].shift(1).rolling(60, min_periods=30).min()) - 1
        sig = ret / vol
        sig = ts_rank(sig, 242 * 2)
        sig = sig.rolling(5, min_periods=2).mean()
        sig[sig <= -0.5] = 0
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)

##########
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 14:38:31 2021

@author: appadmin
"""
import pandas as pd
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *
import numpy as np

class CFG30_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_hs300', 'weight_boolean_hs300', 'close_hs300']

        super(CFG30_CC_IF, self).__init__(required_columns=required_columns
                                  )
        
    def on_bar(self, data):
        df_s = data['amount_hs300'].rolling(60, min_periods = 15).sum()
        df_s = df_s[data['weight_boolean_hs300']]
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)

        upclose = (data['close_hs300'][bool_df]>data['close_hs300'][bool_df].shift(1)).sum(axis = 1)
        downclose = (data['close_hs300'][bool_df]<data['close_hs300'][bool_df].shift(1)).sum(axis = 1)
        t_prcd2 = (((upclose-downclose)/ (upclose+downclose)).rolling(45, min_periods = 15).mean())
        
        t_prcd2 = t_prcd2.replace([-np.inf,np.inf], np.nan)

        factor = t_prcd2.to_frame()
        factor.columns = [self.__class__.__name__]
        #factor = factor.between_time('13:00', '14:49').groupby(pd.TimeGrouper('D')).mean().dropna(how = 'all')
        factor = ts_rank(factor)
        factor[factor<0] = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 14:26:40 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator

class LCCorr_ind_ICIF_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot', 'low_spot']

        super(LCCorr_ind_ICIF_CC_IF, self).__init__(
                                  required_columns=required_columns)


    def on_bar(self, data):

        high = data['low_spot']
        close = data['close_spot']
        s = high.rolling(60, min_periods=30).std()
        f = close.rolling(60, min_periods=30).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        t_chgpcor2 = high.rolling(60, min_periods=30).cov(close) / (s * f)
        factor = t_chgpcor2.to_frame()

        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor.rolling(5, min_periods = 2).mean())
        factor = ts_rank(factor)
        return factor

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


def log(df1):
    output = np.log(df1[df1 > 0])
    return output


def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    return rolling_table


def ts_decay_linear(df1, d):
    # weighted moving average over the past d periods
    # linearly decaying weights d, d – 1, …, 1 (rescaled to sum up to 1)
    output = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
    weight = np.arange(d) + 1
    for i in df1.columns:
        temp_y = df1[i].values
        temp_y = rolling_window(temp_y, d)
        temp_x = np.tile(weight, (temp_y.shape[0], 1))
        flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
        flag = np.where(flag <= d - int(d / 2), 1, np.nan)
        output[i].iloc[d - 1:] = ((temp_y * temp_x).sum(axis=1) / temp_x.sum(axis=1)) * flag
    return output


class wsc_search7_if(FactorGenerator):
    def __init__(self):
        super(wsc_search7_if, self).__init__(required_columns=['volume', 'recent_month_mask'],
                                             lookback_bars=2000)

    def on_bar(self, data):
        # 算法搜索
        mask = data['recent_month_mask']
        data = data['volume']
        factor1 = log(data)
        factor = ts_decay_linear(factor1, 55)
        factor = rolling_norm(factor, 1000)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    return rolling_table


def reg_beta(df1, d):
    # 过去d期A对1:d回归的回归系数
    output = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
    for i in df1.columns:
        temp_y = df1[i].values
        temp_y = rolling_window(temp_y, d)
        temp_x = np.tile(np.arange(d) + 1, (temp_y.shape[0], 1))
        y = np.nansum((temp_y.T - np.nanmean(temp_y, axis=1).T) * (temp_x.T - np.nanmean(temp_x, axis=1).T), axis=0)
        x = np.nansum((temp_x.T - np.nanmean(temp_x, axis=1).T) ** 2, axis=0)
        flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
        flag = np.where(flag <= d - int(d / 2), 1, np.nan)
        output[i].iloc[d - 1:] = (y / x) * flag
    return output



def ts_max(df1, d):
    # moving time-series average for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_max(df1, window=d, min_count=int(d/2), axis=0),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_max(df1, window=d, min_count=int(d/2), axis=0),
                      index=df1.index, name=df1.name)
    return output


def ts_min(df1, d):
    # moving time-series average for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_min(df1, window=d, min_count=int(d/2), axis=0),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_min(df1, window=d, min_count=int(d/2), axis=0),
                      index=df1.index, name=df1.name)
    return output


def ts_mean(df1, d):
    # moving time-series average for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_mean(df1, window=d, min_count=int(d/2), axis=0),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_mean(df1, window=d, min_count=int(d/2), axis=0),
                      index=df1.index, name=df1.name)
    return output


def ts_sum(df1, d):
    # moving time-series average for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_sum(df1, window=d, min_count=int(d/2), axis=0),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_sum(df1, window=d, min_count=int(d/2), axis=0),
                           index=df1.index, name=df1.name)
    return output


def ts_delta(df1, d):
    # A_i - A_(i-d)
    output = df1.diff(periods=d)
    return output


class wsc10_spot_kpz_if(FactorGenerator):
    def __init__(self):
        super(wsc10_spot_kpz_if, self).__init__(required_columns=['close_spot', 'high_spot', 'low_spot'],
                                                lookback_bars=2000)

    def on_bar(self, data):
        close = data['close_spot']
        high = data['high_spot']
        low = data['low_spot']
        n = 30
        hl = high + low
        high_abs = abs(ts_delta(high, 1))
        low_abs = abs(ts_delta(low, 1))
        dmz = np.maximum(high_abs, low_abs)
        dmz[ts_delta(hl, 1)<=0] = 0
        dmf = np.maximum(high_abs, low_abs)
        dmf[ts_delta(hl, 1)>=0] = 0
        a = ts_sum(dmz, n) + ts_sum(dmf, n)
        a[abs(a)<1e-8] = np.nan
        ddi = (ts_sum(dmz, n) - ts_sum(dmf, n)) / a
        factor = ts_mean(ddi, 60)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = ts_rank(factor, 1200)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        factor[factor <= -0.5] = 0
        #factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 11:10:27 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class VwapLSVol_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['vwap_if', 'recent_month_mask']

        super(VwapLSVol_CC_IF, self).__init__(
                                  required_columns=required_columns)

    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa

    def on_bar(self, data):

        a = data['vwap_if'].rolling(45, min_periods = 15).std()
        a[abs(a) < 1e-8] = np.nan
        prstd_r = -data['vwap_if'].rolling(1200, min_periods = 600).std()/a
        factor = prstd_r[data['recent_month_mask']].mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc8_cfg_as_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc8_cfg_as_if, self).__init__(required_columns=['close_hs300', 'volume_hs300', 'weight_boolean_hs300', 'amount_hs300'],
                                             lookback_bars=2000)

    def on_bar(self, data):
        # mask
        bool_mask = data['weight_boolean_hs300']
        amount_mask = data['amount_hs300'][bool_mask]

        # close和volume的价量背离
        stk_close = data['close_hs300']
        stk_volume = data['volume_hs300']
        factor_init = stk_close.rolling(55, min_periods=15).cov(stk_volume)
        factor_raw = (factor_init * amount_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        factor = ts_rank(factor_mean, 240*3)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 15:24:58 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator import FactorGenerator

class RolTrendLS_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['close_if', 'low_if', 'high_if', 'recent_month_mask']

        super(RolTrendLS_CC_IF, self).__init__(
                                  required_columns=required_columns)
        


    def on_bar(self, data):

        ll = (data['close_if'] - data['low_if'].rolling(120, min_periods = 15).min())-(data['high_if'].rolling(120, min_periods = 15).max() - data['low_if'].rolling(60, min_periods = 15).min())
        a2 = ll.rolling(10, min_periods = 5).mean()
        a3 = a2.rolling(10, min_periods = 5).mean()
        vwtc_r = 3*a3-2*a2
        factor = vwtc_r[data['recent_month_mask']].mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        return factor


##########
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 15:38:45 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator

class SYXWR_ind_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot_if', 'low_spot_if', 'open_spot_if', 'high_spot_if']

        super(SYXWR_ind_CC_IF, self).__init__(
                                  required_columns=required_columns)

    


    def on_bar(self, data):

        temp1 = pd.Series(np.where(data['open_spot_if']>data['close_spot_if'], data['open_spot_if'], data['close_spot_if']))
        temp2 = pd.Series(np.where(data['open_spot_if']>data['close_spot_if'], data['close_spot_if'], data['open_spot_if']))
        temp1.index = data['open_spot_if'].index
        temp2.index = data['open_spot_if'].index
        a = (data['high_spot_if'] - temp1).rolling(35, min_periods = 15).mean()
        b = (data['high_spot_if'].rolling(35, min_periods = 15).max()-data['low_spot_if'].rolling(35, min_periods = 15).min())
        a[abs(a) < 1e-8] = np.nan
        b[abs(b) < 1e-8] = np.nan
        t_pcor = (data['high_spot_if']-temp1)/a
        t_pcor2 = (data['close_spot_if']-data['low_spot_if'].rolling(35, min_periods = 15).min())/b
        t_pcorr = (t_pcor2 - t_pcor).rolling(60, min_periods = 20).mean()
        factor = t_pcorr.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc7_cfg_ar_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc7_cfg_ar_if, self).__init__(required_columns=['close_hs300', 'weight_boolean_hs300', 'amount_hs300'],
                                             lookback_bars=2000)

    def on_bar(self, data):
        # mask
        bool_mask = data['weight_boolean_hs300']
        amount_mask = data['amount_hs300'][bool_mask]
        amount_rank_mask = 2 * amount_mask.rank(axis=1, pct=True) - 1

        # as follows
        stk_close = data['close_hs300']
        stk_ret = ts_pct_change(stk_close, 5)
        b = ts_mean(stk_ret, 30)
        c = ts_std(stk_ret, 30)
        factor_init = 3 * b + c
        factor_raw = (factor_init * amount_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 35)
        factor = ts_rank(factor_mean, 240*5)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 13:28:50 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex

class LMLS_nr_t3_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_boolean_hs300', 'low_hs300', 'turnover_hs300', 'close_hs300']

        super(LMLS_nr_t3_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    
    def on_bar(self, df):

        turnover = (df['turnover_hs300'].rolling(60, min_periods = 15).mean())[df['weight_boolean_hs300']]

        ret = (df['close_hs300']/df['close_hs300'].shift(30)-1)[df['weight_boolean_hs300']]
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)
        temp6 = ret.gt(pd.Series(ret.quantile(0.80, axis = 1)), axis=0)
        mask = temp4*temp6
        
        temp = df['low_hs300'].rolling(60, min_periods = 15).mean() - df['low_hs300'].shift(15).rolling(45, min_periods = 7).mean()
        temp = rolling_norm(temp)
        tempdf = (temp*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(15, min_periods = 8).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np

class wyc_gain_high_spot_if(FactorGenerator):
    def __init__(self):
        required_columns=['high_spot_if', 'close_spot_if']
        lookback_bars=2000
        super(wyc_gain_high_spot_if, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        high = df['high_spot_if']
        close = df['close_spot_if']
        N = 30
        gain_high_60 = high / high.shift(N) - 1
        h_c = close / high - 1
        a = mean(h_c, N)
        a[abs(a) < 1e-8] = np.nan
        factor = ts_sum(gain_high_60 / a, N)
        factor = mean(factor, N) * -1
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        factor.loc[factor[columnname] <= -0.5] = 0

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 13:48:16 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex

class ClMaxClMin_nr_wt_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_hs300','weight_boolean_hs300', 'close_hs300', 'turnover_hs300']

        super(ClMaxClMin_nr_wt_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, df):
        stk_weight = (df['weight_hs300'])[df['weight_boolean_hs300']]
        turnover = (df['turnover_hs300'].rolling(60, min_periods = 15).mean())[df['weight_boolean_hs300']]
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)
        
        mask = stk_weight*temp4
        m_vwap_ind_r = (df['close_hs300']).rolling(45, min_periods = 30).max()/df['close_hs300'].rolling(45, min_periods = 30).min()
        m_vwap_ind_r[np.abs(m_vwap_ind_r)>10000] = np.nan
        temp = rolling_norm(m_vwap_ind_r, 242*5)
        tempdf = (temp*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(5, min_periods = 2).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 11:15:57 2020

@author: appadmin
"""
import pandas as pd
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *
import numpy as np

class CFG29_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_hs300', 'weight_boolean_hs300', 'close_hs300']

        super(CFG29_CC_IF, self).__init__(required_columns=required_columns)
        
    def on_bar(self, data):

         #448_LINEARREG_SLOPE(ts_max(twap, 40), 50)
        columnname = self.__class__.__name__
        temp1 = data['close_hs300'].rolling(35, min_periods = 20).max()
        holder = {}
        for item in temp1.columns:
            close_spot = (temp1[item]).values
            x = np.array(range(len(data['close_hs300'][item])))
            #print(item)
            holder[item] = pd.Series(rolling_linear_reg(x, close_spot, 35))

        temp = pd.DataFrame(holder)
        temp.index = data['close_hs300'].index
        

        temp = (temp[data['weight_boolean_hs300']]).mean(axis = 1)
        cc3 = ts_rank(temp.to_frame(), 400)
        cc3.columns = [columnname]

        return cc3
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 16 14:46:59 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class L123_nr_ac_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_hs300', 'close_spot_if', 'close_hs300', 'weight_boolean_hs300', 'low_hs300']
        super(L123_nr_ac_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, data):
        df_s = (data['amount_hs300'].rolling(120, min_periods = 15).sum())[data['weight_boolean_hs300']]
        stk_close = data['close_hs300']
        index_close = data['close_spot_if']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        stk_index_corr = stk_index_corr[data['weight_boolean_hs300']]
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0)
        temp2 = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.80, axis = 1)), axis=0)
        mask = temp1*temp2
        
        hlow = data['low_hs300']
        i11 = (hlow.rolling(10, min_periods = 5).min()-hlow.rolling(25, min_periods = 10).min())
        i12 = hlow.rolling(20, min_periods = 15).min()-hlow.rolling(30, min_periods = 10).min()
        i2 = (i11-i12)
        i2 = rolling_norm(i2, 242*5)
        #i2[np.abs(i2)>1] = np.nan
        tempdf = (i2*mask)
        tempdf = tempdf.mean(axis = 1).to_frame()
        factor = tempdf.rolling(45, min_periods = 23).mean()
        factor = ts_rank(factor)
        
        factor.columns = [self.__class__.__name__]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 14:23:00 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class LSC_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['high_if', 'low_if', 'close_if', 'recent_month_mask']

        super(LSC_CC_IF, self).__init__(
                                  required_columns=required_columns)

    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa

    def on_bar(self, data):

        a = (data['high_if'].rolling(30, min_periods = 10).max() - data['low_if'].rolling(30, min_periods = 10).min())
        b = (data['high_if'].rolling(30, min_periods = 10).max() - data['low_if'].rolling(30, min_periods = 10).min())
        a[abs(a) < 1e-8] = np.nan
        b[abs(b) < 1e-8] = np.nan
        hh = (data['high_if'].rolling(30, min_periods = 10).max() - data['close_if'])/a
        ll = (data['close_if'] - data['low_if'].rolling(30, min_periods = 10).min())/b
        vwtc_r = ll.rolling(90, min_periods = 15).mean()-hh.rolling(90, min_periods = 15).mean()
        factor = vwtc_r[data['recent_month_mask']].mean(axis = 1).to_frame()

        factor.columns = [self.__class__.__name__]
        factor = self.normalization(factor)
        factor[factor<=-0.5] = 0
        factor[factor>1] = 0
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc21_cfg_ar_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc21_cfg_ar_if, self).__init__(required_columns=['close_hs300', 'high_hs300', 'low_hs300', 'open_hs300', 'amount_hs300', 'weight_boolean_hs300'],
                                              lookback_bars=2000)

    def on_bar(self, data):
        # mask
        stk_amount = data['amount_hs300']
        bool_mask = data['weight_boolean_hs300']
        amount_mask = stk_amount[bool_mask]
        amount_rank_mask = 2 * amount_mask.rank(axis=1, pct=True) - 1

        # 根据asi指标改造而来
        # asi指标由si累加而来，但这样会导致每个时刻累加的起点不同，因此用si过去一段时间的移动平均代替，解决起点不同的问题
        stk_close = data['close_hs300']
        stk_high = data['high_hs300']
        stk_low = data['low_hs300']
        stk_open = data['open_hs300']
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
        r4 = r2.copy(deep=True)
        r4[(a>=b)&(a>=c)] = r1
        r = r4.copy(deep=True)
        r[(c>=a)&(c>=b)] = r3
        r[abs(r)<1e-8] = np.nan
        m[abs(m)<1e-8] = np.nan
        si = 50 * (ts_delta(stk_close, 1) + ts_delay(stk_close, 1) - ts_delay(stk_open, 1) + 0.5*(stk_close - stk_open)) / r * k / m
        factor_init = si

        factor_raw = (factor_init * amount_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 65)
        factor = ts_rank(factor_mean, 240*6)
        
        factor = factor.to_frame() 
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= 0] = 0
        #factor[factor>=0.5] = np.nan
        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts47_future_nr_tr_if(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_hs300'
        required_columns=['close' + suffix,'turnover' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(wyc_ts47_future_nr_tr_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_hs300'
        columnname = self.__class__.__name__

        con1 = df['close' + suffix] > delay(df['close' + suffix], 1)
        factor = con1.rolling(100).sum()
        factor = ts_mean(factor, 20)

        factor = rolling_normalize(factor, 5 * 242)

        t = df['turnover' + suffix][df['weight_boolean' + suffix]]
        tr = (2 * t.rank(axis=1, pct=True) - 1)
        factor = factor * tr
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank_bk(factor, 300)
        factor = ts_mean(factor, 10)
        factor = ts_rank_bk(factor, 5 * 242)
        factor.columns = [columnname]

        factor[factor < 0] = 0

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 14:33:13 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator


class L123_ICIF_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns=['low', 'recent_month_mask']

        super(L123_ICIF_CC_IF, self).__init__(required_columns=required_columns)
    

    

    
    def on_bar(self, df):
        columnname = self.__class__.__name__
        hlow = df['low']
        i11 = (hlow.rolling(10, min_periods = 5).min()-hlow.rolling(25, min_periods = 10).min())
        i12 = hlow.rolling(20, min_periods = 15).min()-hlow.rolling(30, min_periods = 10).min()
        i2 = (i11-i12).rolling(30, min_periods = 20).mean()
        i2 = ts_rank(i2[df['recent_month_mask']].mean(axis = 1).to_frame())
        #i2 = rolling_norm(i2)
        i2[i2>1] = 0
        i2[i2<=-0.5] = 0
        i2.columns = [columnname]    
        return i2
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 14:26:47 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator

class LminC_ind_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot_if', 'low_spot_if']

        super(LminC_ind_CC_IF, self).__init__(
                                  required_columns=required_columns)
    


    def on_bar(self, data):

        lltc_ind_r = -data['low_spot_if'].rolling(180, min_periods = 90).min()/(data['close_spot_if'])
        factor = lltc_ind_r.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        factor[factor<-0.8] = 0
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *
from help_functions_wsc import replace_zero


    
class wsc_hf18_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_hf18_if, self).__init__(required_columns=['Bid1AmtMean_300', 'Buy1NumOrdersMean_300', 'weight_300'],
                                          lookback_bars=3000)

    def on_bar(self, hf_data):
        # 买一挂单金额除以买一挂单数量，表征平均一单的挂单金额，还是大小单逻辑
        weight_300 = hf_data['weight_300']
        temp = hf_data['Buy1NumOrdersMean_300'].copy()
        temp = replace_zero(temp)
        factor_raw = (hf_data['Bid1AmtMean_300'] / temp * weight_300).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 20)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= 0] = 0
        # factor[factor>=0] = 0
        return factor
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


class wsc_cfg7_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_cfg7_if, self).__init__(required_columns=['close_hs300', 'weight_hs300', 'amount_hs300', 'weight_boolean_hs300'],
                                          lookback_bars=2000)

    def on_bar(self, data):
        # factor logic
        bool_mask = data['weight_boolean_hs300']
        stk_close = data['close_hs300']
        stk_amt = data['amount_hs300'][bool_mask]
        stk_ret = stk_close.pct_change(3, fill_method=None)[bool_mask]
        stk_ret_long = stk_ret.gt(stk_ret.quantile(0.8, axis=1), axis=0)
        factor = stk_amt[stk_ret_long]
        factor = (factor * data['weight_hs300']).sum(axis=1)
        factor = factor.rolling(20, min_periods=7).mean()

        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = ts_rank(factor, 200*6)
        factor[factor<=-0.5] = 0
        #factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *


class wyc_if_2hour_return_nr_ts_if(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_hs300'
        required_columns=['close' + suffix,'turnover' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(wyc_if_2hour_return_nr_ts_if, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        suffix = '_hs300'
        stk_close = df['close' + suffix]
        stk_close[abs(stk_close) < 1e-8] = np.nan
        ifreturn = df['close' + suffix] / stk_close.shift(1) - 1
        factor = ts_mean(ifreturn, 200)

        factor = rolling_norm(factor, 5 * 242)

        t = df['turnover' + suffix][df['weight_boolean' + suffix]]
        factor = factor * t
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 100)
        factor = ts_mean(factor, 20)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]


        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 13:18:16 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex

class cd_ind_nr_at_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_hs300','weight_boolean_hs300', 'close_hs300', 'turnover_hs300']

        super(cd_ind_nr_at_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, data):

        turnover = (data['turnover_hs300'].rolling(60, min_periods = 15).mean())[data['weight_boolean_hs300']]
        df_s = (data['amount_hs300'].rolling(120, min_periods = 15).sum())[data['weight_boolean_hs300']]
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0)
        #temp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0)
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)
        mask = temp1*temp4
        
        temp = data['close_hs300'].rolling(60, min_periods = 2).mean().diff()
        temp = rolling_norm(temp, 242*5)
        tempdf = (temp*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(10, min_periods = 5).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor
##########
from factor_generator import FactorGenerator
from operators_wsc import *



class wsc_ti5_if(FactorGenerator):
    def __init__(self):
        super(wsc_ti5_if, self).__init__(required_columns=['close_if', 'recent_month_mask'],
                                         lookback_bars=2000)

    def on_bar(self, data_dict):
        # 布林带修正后的收益率
        index_close = data_dict['close_if']
        future_mask = data_dict['recent_month_mask']
        close_mean = ts_mean(index_close, 40)
        close_std = ts_std(index_close, 40)
        factor_raw = ts_pct_change(close_mean + 2 * close_std, 40).replace([-np.inf, np.inf], np.nan)
        factor = ts_rank(factor_raw, 1200)
        factor = factor[future_mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


def ts_std(df1, d):
    # moving time-series standard deviation over the past d periods
    output = pd.DataFrame(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                          index=df1.index, columns=df1.columns)
    return output


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


class wsc_search3_if(FactorGenerator):
    def __init__(self):
        super(wsc_search3_if, self).__init__(required_columns=['high_spot'],
                                             lookback_bars=2000)

    def on_bar(self, data):
        # 算法搜索
        data = data['high_spot'].to_frame()
        factor = ts_std(data, 75)

        # factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = ts_rank(factor, 600 * 2)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc3_cfg_cr_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc3_cfg_cr_if, self).__init__(required_columns=['close_hs300', 'open_hs300', 'high_hs300', 'low_hs300', 'stk_index_corr_hs300'],
                                             lookback_bars=2000)

    def on_bar(self, data):
        # mask
        corr_mask = data['stk_index_corr_hs300']
        corr_rank_mask = 2 * corr_mask.rank(axis=1, pct=True) - 1

        # 用(close-open)/(high-low)衡量一分钟内的股价波动
        stk_close = data['close_hs300']
        stk_open = data['open_hs300']
        stk_high = data['high_hs300']
        stk_low = data['low_hs300']        
        a = stk_high - stk_low
        a[abs(a)<1e-8] = np.nan
        b = stk_close - stk_open
        b[b<0] = np.nan
        factor_init = ts_sum(b/a, 60)
        factor_raw = (factor_init * corr_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 20)
        factor = ts_rank(factor_mean, 1200)
        factor[factor<=-0.5] = 0
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor

##########
from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np

class wyc_icif_if(FactorGenerator):
    def __init__(self):
        required_columns=['close_if','close','recent_month_mask']
        lookback_bars=2000
        super(wyc_icif_if, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        mask = df['recent_month_mask']
        factor = df['close'] - df['close_if']
        factor = factor - mean(factor, 60)
        factor = mean(factor, 20)
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor.loc[factor[columnname] <= 0] = 0

        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk


class wyc_ts19_icfuture_if(FactorGenerator):
    def __init__(self):

        required_columns=['close','low','high','volume', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts19_icfuture_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self,df):
        columnname = self.__class__.__name__
        mask = df['recent_month_mask']
        a = (df['high'] - df['low'])
        a[abs(a) < 1e-8] = np.nan
        factor = ts_sum(((df['close'] - df['low']) - (df['high'] - df['close'])) / a * df['volume'], 20)
        # factor = ts_rank(factor, 60)
        factor = ts_mean(factor, 30)
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 1200)
        factor = factor[mask].sum(axis=1).to_frame()

        factor.columns = [columnname]

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 14:27:25 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class LminLmean_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns =['low_if', 'recent_month_mask']
        super(LminLmean_CC_IF, self).__init__(
                                  required_columns=required_columns)
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
        
    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa
    
    def on_bar(self, data):

        ctl_r = -data['low_if'].rolling(90, min_periods =15).min()/data['low_if'].rolling(15, min_periods =5).mean()
        factor = ctl_r[data['recent_month_mask']].mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factor = self.normalization(factor, 242*2)
        factor[factor<-1] =0
        factor[factor>1] = 0
        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np


class wyc_icifih_mul_if(FactorGenerator):
    def __init__(self):
        required_columns=['close_spot','close_spot_if','close_spot_ih']
        lookback_bars=2000
        super(wyc_icifih_mul_if, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        factor = df['close_spot'] - 2 * df['close_spot_ih'] + df['close_spot_if']
        factor = factor - mean(factor, 200)
        factor = factor.to_frame()
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_norm(factor, 5 * 242)
        factor.loc[factor[columnname] <= 0] = 0
        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np


class wyc_ts44_spot_if(FactorGenerator):
    def __init__(self):
        required_columns = ['volume_spot_if', 'close_spot_if']
        lookback_bars = 2000
        super(wyc_ts44_spot_if, self).__init__(
            required_columns=required_columns,
            lookback_bars=lookback_bars)

    def on_bar(self, df):
        temp1 = df['volume_spot_if'].copy(deep=True)
        con1 = df['close_spot_if'] > delay(df['close_spot_if'], 1)
        con2 = df['close_spot_if'] < delay(df['close_spot_if'], 1)
        temp1[con2] = -1 * df['volume_spot_if']
        factor = ts_sum(temp1, 25)
        factor = mean(factor, 40)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_norm(factor, 5 * 242)
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 10:36:54 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex

class LminC_nr_rl_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_boolean_hs300', 'low_hs300', 'turnover_hs300', 'close_hs300']

        super(LminC_nr_rl_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, df):
        tt = df['turnover_hs300']
        tt[abs(tt) < 1e-8] = np.nan
        ret_30 = (df['turnover_hs300']/tt.shift(30)-1)[df['weight_boolean_hs300']]
        ret_select = ret_30.gt(pd.Series(ret_30.quantile(0.90, axis = 1)), axis=0)   
        mask = ret_select
        
        lltc_ind_r = -df['low_hs300'].rolling(180, min_periods = 90).min()/(df['close_hs300'])
        lltc_ind_r = rolling_norm(lltc_ind_r)
        tempdf = (lltc_ind_r*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(15, min_periods = 8).mean()
        factor = ts_rank(factor)
        factor[factor<= 0] = 0
        factor.columns = [self.__class__.__name__]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 13:26:19 2020

@author: appadmin
"""

import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex

class HHLS_nr_vt_CC_CFG_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_boolean_hs300',  'high_hs300', 'close_hs300', 'turnover_hs300']

        super(HHLS_nr_vt_CC_CFG_IF, self).__init__(required_columns=required_columns
                                  )
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa
    
    def ts_std(self, df1, d):
        # moving time-series rank for the past d periods
        if isinstance(df1, pd.DataFrame):
            output = pd.DataFrame(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                                  index=df1.index, columns=df1.columns)
        elif isinstance(df1, pd.Series):
            output = pd.Series(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                               index=df1.index, name=df1.name)
        return output
    
    def on_bar(self, data):
        stk_close = data['close_hs300']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = self.ts_std(stk_ret, 30)
        stk_volatility = stk_volatility[data['weight_boolean_hs300']]
        turnover = (data['turnover_hs300'].rolling(60, min_periods = 15).mean())[data['weight_boolean_hs300']]
        temp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0)
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)
        mask = temp3*temp4
        temp = data['high_hs300'].rolling(50, min_periods = 15).max() - data['high_hs300'].shift(50).rolling(50, min_periods = 7).max()
        temp = self.normalization(temp)
        tempdf = (temp*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(10, min_periods = 5).mean()
        factor = self.ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor
##########
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np
from functools import partial


def place_back_format(dat_mat, dat_orig):
    if isinstance(dat_orig, pd.DataFrame):
        dat_fmt = pd.DataFrame(dat_mat, index=dat_orig.index, columns=dat_orig.columns)
    elif isinstance(dat_orig, pd.Series):
        dat_fmt = pd.Series(dat_mat, index=dat_orig.index)
        dat_fmt.name = dat_orig.name
    else:
        dat_fmt = dat_mat
    return dat_fmt


def calc_ts_pct(ts_dat, roll_win=20, min_pct=1, force_range=False):
    min_win = int(min_pct * roll_win)
    ts_dat_pct_np = bk.move_rank(ts_dat, window=roll_win, min_count=min_win, axis=0)
    if force_range:
        ts_dat_pct_np = (ts_dat_pct_np + 1) / 2
    ts_dat_pct = place_back_format(ts_dat_pct_np, ts_dat)
    return ts_dat_pct


def calc_change_helper(score_raw, short_win, long_win, ts_pct_win, sign=1, min_pct=0.9):
    score_change_raw = sign * (
            score_raw.rolling(short_win, int(min_pct * short_win)).mean() - score_raw.rolling(long_win, int(
        min_pct * long_win)).mean())
    score_change = calc_ts_pct(score_change_raw, ts_pct_win, min_pct=min_pct)
    return score_change


def calc_std_helper(score_raw, std_win, ts_pct_win, min_pct=0.9):
    score_std_raw = score_raw.rolling(std_win, int(min_pct * std_win)).std()
    score_std = calc_ts_pct(score_std_raw, ts_pct_win)
    return score_std


def calc_ma_helper(score_raw, ma_win, ts_pct_win, min_pct=0.9):
    score_ma_raw = score_raw.rolling(ma_win, int(min_pct * ma_win)).mean()
    score_ma = calc_ts_pct(score_ma_raw, ts_pct_win, min_pct=min_pct)
    return score_ma


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


class stk2idx_ret_range_corr_zsj_if(FactorGeneratorComplex):
    def __init__(self):
        super(stk2idx_ret_range_corr_zsj_if, self).__init__(required_columns=['close_hs300', 'high_hs300', 'low_hs300', 'weight_boolean_hs300'],
                                                            lookback_bars=2000)

    def on_bar(self, data):
        ## prep data
        stk_close = data['close_hs300']
        bool_mask = data['weight_boolean_hs300']

        # factor logic
        stk_high = data['high_hs300']
        stk_low = data['low_hs300']
        ma_win = 55
        ts_pct_win = 1200
        min_pct = 0.9
        stk_ret_range = stk_high/stk_low - 1
        stk_ret = stk_close/stk_close.shift(1) - 1
        ret_range_corr_raw = stk_ret[bool_mask].corrwith(stk_ret_range[bool_mask], axis=1)
        stk2idx_ret_range_corr = calc_ma_helper(ret_range_corr_raw,ma_win,ts_pct_win,min_pct)
        factor = stk2idx_ret_range_corr.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 15:03:17 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex

class HL123_tr_CC_CFG_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_boolean_hs300', 'turnover_hs300', 'high_hs300', 'low_hs300']

        super(HL123_tr_CC_CFG_IF, self).__init__(required_columns=required_columns
                                  )
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa
    
    def ts_std(self, df1, d):
        # moving time-series rank for the past d periods
        if isinstance(df1, pd.DataFrame):
            output = pd.DataFrame(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                                  index=df1.index, columns=df1.columns)
        elif isinstance(df1, pd.Series):
            output = pd.Series(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                               index=df1.index, name=df1.name)
        return output
    
    def on_bar(self, data):
        
        turnover = (data['turnover_hs300'].rolling(60, min_periods = 15).mean())[data['weight_boolean_hs300']]
        turnover_rank = 2 * turnover.rank(axis=1, pct=True) - 1
        
        mask = turnover_rank
        hlow = data['low_hs300']
        hhigh = data['high_hs300']
        i11 = hhigh.rolling(10, min_periods = 5).max()-hlow.rolling(60, min_periods = 10).min()
        i12 = (hhigh.shift(30)).rolling(10, min_periods = 5).max()-(hlow.shift(30)).rolling(60, min_periods = 10).min()
        i2 = (i11-i12)
        tempdf = (i2*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(30, min_periods = 15).mean()
        factor = self.ts_rank(factor, 2400)
        factor.columns = [self.__class__.__name__]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 11:10:24 2020

@author: appadmin
"""
from factor_generator import FactorGenerator
from operators_cc import *
import pandas as pd
import numpy as np

class CPLR_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot_if']
 
        super(CPLR_CC_IF, self).__init__(
                                  required_columns=required_columns)
        
    def on_bar(self, data):
        #LINEARREG_SLOPE(ts_max(close_spot, 40), 70)
        
        x = np.array(range(len(data['close_spot_if'])))
        temp = data['close_spot_if'].rolling(40, min_periods = 20).max()
        factor = pd.Series(rolling_linear_reg(x, temp, 75))
        factor.index = data['close_spot_if'].index
        
        factor = ts_rank(factor.to_frame(), 242*2)
        factor.columns = [self.__class__.__name__]
        #factor[factor<-0] = 0
        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk



class wyc_ts14_future_wr_if(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_hs300'
        required_columns=['close' + suffix, 'weight' + suffix]
        lookback_bars=2000
        super(wyc_ts14_future_wr_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        suffix = '_hs300'
        key = 'close' + suffix
        factor = pd.DataFrame(np.where(df[key] > delay(df[key], 2), std(df[key], 50), 0),
                              index=df[key].index, columns=df[key].columns)
        factor = ts_mean(factor, 30)

        wr = (2 * df['weight' + suffix].rank(axis=1, pct=True) - 1)
        factor = factor * wr
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank_bk(factor, 5 * 242)
        factor.columns = [columnname]

        factor[factor < 0] = 0

        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk



class wyc_ts29_icfuture_if(FactorGenerator):
    def __init__(self):
        lookback_bars = 2000
        required_columns = ['close', 'volume', 'recent_month_mask']
        super(wyc_ts29_icfuture_if, self).__init__(
            required_columns=required_columns,
            lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        mask = df['recent_month_mask']
        N = 20
        dfclose = df['close']
        dfclose[abs(dfclose) < 1e-8] = np.nan
        factor = (df['close'] - delay(df['close'], N)) / delay(dfclose, N) * df['volume']
        factor = ts_rank(factor, 300)
        factor = ts_mean(factor, 20)
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 5 * 242)
        factor = factor[mask].sum(axis=1).to_frame()

        factor.columns = [columnname]
        factor[factor <= -0.5] = 0

        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import numpy as np

class xdy_ts2_spot_nr_tr_if(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_hs300'
        required_columns=['high' + suffix, 'low' + suffix,'turnover' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(xdy_ts2_spot_nr_tr_if, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_hs300'
        columnname = self.__class__.__name__

        high = df['high' + suffix]
        low = df['low' + suffix]
        high[abs(high) < 1e-8] = np.nan
        gain_high_20 = high / high.shift(20) - 1
        factor = low * gain_high_20
        factor = multi_processing_joblib(df=factor, func=ts_truncated_ema, n_jobs=-1, d=200, alpha= 1/26)

        factor = rolling_norm(factor, 5 * 242)

        t = df['turnover' + suffix][df['weight_boolean' + suffix]]
        tr = (2 * t.rank(axis=1, pct=True) - 1)
        factor = factor * tr
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 300)
        factor = ts_mean(factor, 10)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        factor[factor<0] = 0

        return factor
##########
from factor_generator import FactorGenerator
import pandas as pd
import numpy as np
import bottleneck as bk

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

class tr1_zf_if(FactorGenerator):
    def __init__(self):
        required_columns = ['high_spot_if', 'low_spot_if', 'close_spot_if']
        super(tr1_zf_if, self).__init__(required_columns=required_columns)

    def on_bar(self, data):
        hh = data['high_spot_if'].rolling(121*2, min_periods=30).max()
        ll = data['low_spot_if'].rolling(121*2, min_periods=30).min()
        hhll = hh + ll
        hhll[abs(hhll) < 1e-8] = np.nan
        sig = 2 * data['close_spot_if'] / hhll
        sig = rolling_norm(sig, 242 * 3)
        sig[sig<=-0.5] = 0
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)

##########
from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np


def rolling_normalize(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


def ts_position(x, t):
    def get_position(ylist):
        smin = min(ylist)
        smax = max(ylist)
        y = ylist[-1]
        return (y - smin) / (smax - smin)

    return x.rolling(t, min_periods=t // 2).apply(get_position)


class xdy_ts4_future_if(FactorGenerator):
    def __init__(self):
        required_columns = ['high_if', 'recent_month_mask']
        lookback_bars = 2000
        super(xdy_ts4_future_if, self).__init__(required_columns=required_columns,
                                                lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        high = df['high_if']
        factor = ts_position(high, 7)
        factor = -1 * factor.rolling(75, min_periods=20).skew()
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        mask = df['recent_month_mask']
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor.loc[factor[columnname] <= -0.5] = 0

        return factor

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    return rolling_table


def reg_beta(df1, d):
    # 过去d期A对1:d回归的回归系数
    output = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
    for i in df1.columns:
        temp_y = df1[i].values
        temp_y = rolling_window(temp_y, d)
        temp_x = np.tile(np.arange(d) + 1, (temp_y.shape[0], 1))
        y = np.nansum((temp_y.T - np.nanmean(temp_y, axis=1).T) * (temp_x.T - np.nanmean(temp_x, axis=1).T), axis=0)
        x = np.nansum((temp_x.T - np.nanmean(temp_x, axis=1).T) ** 2, axis=0)
        flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
        flag = np.where(flag <= d - int(d / 2), 1, np.nan)
        output[i].iloc[d - 1:] = (y / x) * flag
    return output


class wsc3_future_kpz_if(FactorGenerator):
    def __init__(self):
        super(wsc3_future_kpz_if, self).__init__(required_columns=['close', 'recent_month_mask'],
                                                 lookback_bars=2000)

    def on_bar(self, data):
        # 计算过去5分钟收益率的均值和标准差的线性组合
        mask = data['recent_month_mask']
        a = data['close'].pct_change(5, fill_method=None)
        b = a.rolling(45, min_periods=15).mean()
        c = a.rolling(45, min_periods=15).std()
        factor = b + 2 * c
        factor = factor.rolling(10).mean()
        factor = ts_rank(factor, 600*2)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts19_icspot_if(FactorGenerator):
    def __init__(self):

        required_columns=['close_spot','low_spot','high_spot','volume_spot']
        lookback_bars=2000
        super(wyc_ts19_icspot_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        a = (df['high_spot'] - df['low_spot'])
        a[abs(a) < 1e-8] = np.nan
        factor = ts_sum(((df['close_spot'] - df['low_spot']) - (df['high_spot'] - df['close_spot'])) / a * df['volume_spot'], 10)

        factor = ts_rank(factor, 242)
        factor = ts_mean(factor, 120)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_norm(factor, 5 * 242)
        return factor
##########
from factor_generator import FactorGenerator
import pandas as pd
import numpy as np
import bottleneck as bk

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


class mm1_zf_if(FactorGenerator):
    def __init__(self):
        required_columns = ['close_spot_if']
        super(mm1_zf_if, self).__init__(required_columns=required_columns)

    def on_bar(self, data):
        sig = data['close_spot_if']
        sig = rolling_norm(sig, window=60)
        sig = sig.rolling(20, min_periods=5).mean()
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)

##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc1_cfg_ws_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc1_cfg_ws_if, self).__init__(required_columns=['close_hs300', 'close_spot_if', 'weight_hs300'],
                                             lookback_bars=2000)

    def on_bar(self, data):
        # 比较过去一段时间成分股和指数收益率大小，统计那一分钟涨幅小于指数的成分股权重和
        index_return = data['close_spot_if'].pct_change(periods=60, fill_method=None)
        stock_return = data['close_hs300'].pct_change(periods=60, fill_method=None)
        excess_return = (stock_return.subtract(index_return, axis=0))
        excess_return_weight = data['weight_hs300'][excess_return < 0].sum(axis=1)
        excess_return_weight = ts_mean(excess_return_weight, 10)
        factor = ts_rank(excess_return_weight, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 17:25:40 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator

class HcorrC_ind_ICIF_CC_IF(FactorGenerator):
    def __init__(self):
        
        required_columns =['close_spot', 'high_spot']
        
        super(HcorrC_ind_ICIF_CC_IF, self).__init__(
                                  required_columns=required_columns)


    
    def on_bar(self, data):
        high = data['high_spot']
        close = data['close_spot']
        s = high.rolling(45, min_periods=30).std()
        f = close.rolling(45, min_periods=30).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        t_pcor2 = high.rolling(45, min_periods=30).cov(close) / (s * f)
        factor = t_pcor2.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = factor.rolling(30, min_periods = 7).mean()
        factor = ts_rank(factor)  
        return factor



##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np


class wyc_ts47_future_if(FactorGenerator):
    def __init__(self):
        required_columns = ['close_if', 'recent_month_mask']
        lookback_bars = 2000
        super(wyc_ts47_future_if, self).__init__(
            required_columns=required_columns,
            lookback_bars=lookback_bars)

    def on_bar(self, df):
        con1 = df['close_if'] > delay(df['close_if'], 4)
        factor = con1.rolling(50).sum()
        factor = mean(factor, 20)
        mask = df['recent_month_mask']
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc1_cfg_vr_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc1_cfg_vr_if, self).__init__(required_columns=['close_hs300', 'close_spot_if', 'stk_volatility_hs300'],
                                             lookback_bars=2000)

    def on_bar(self, data):
        # mask
        volatility_mask = data['stk_volatility_hs300']
        volatility_rank_mask = 2 * volatility_mask.rank(axis=1, pct=True) - 1

        # 比较过去一段时间成分股和指数收益率大小，统计那一分钟涨幅小于指数的成分股平均波动率打分
        index_return = data['close_spot_if'].pct_change(periods=30, fill_method=None)
        stock_return = data['close_hs300'].pct_change(periods=30, fill_method=None)
        excess_return = (stock_return.subtract(index_return, axis=0))
        excess_return_weight = -volatility_rank_mask[excess_return < 0].mean(axis=1)
        excess_return_weight = ts_mean(excess_return_weight, 45)
        factor = ts_rank(excess_return_weight, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator import FactorGenerator
# from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk


def ts_mean(df1, d):
    # moving time-series average for the past d periods
    output = pd.DataFrame(bk.move_mean(df1, window=d, min_count=int(d / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


def ts_sum(df1, d):
    # moving time-series average for the past d periods
    output = pd.DataFrame(bk.move_mean(df1, window=d, min_count=int(d / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


def delay(df1, d):
    # A_(i-d)
    output = df1.shift(periods=d)
    return output


def rolling_normalize(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


class wyc_ts28_spot_if(FactorGenerator):
    def __init__(self):
        required_columns = ['close_spot_if']
        lookback_bars = 2000
        super(wyc_ts28_spot_if, self).__init__(
            required_columns=required_columns,
            lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        M = 20
        con1 = df['close_spot_if'] > delay(df['close_spot_if'], 10)
        factor = ts_sum(con1.to_frame(), M) / M * 100
        factor = ts_mean(factor, 55)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        factor[factor <= -0.5] = 0

        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc11_cfg_vs_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc11_cfg_vs_if, self).__init__(required_columns=['close_hs300', 'high_hs300', 'low_hs300', 'stk_volatility_hs300'],
                                              lookback_bars=2000)

    def on_bar(self, data):
        # mask
        volatility_mask = data['stk_volatility_hs300']

        # KDJD技术指标，先用stochastics指标衡量收盘价位于最近n分钟的最低价和最高价之间的位置，在以此为基础，计算该指标位于最近m分钟的最大值和最小值之间的位置，作为factor_init。
        stk_close = data['close_hs300']
        stk_high = data['high_hs300']
        stk_low = data['low_hs300']
        n = 30
        m = 150
        low_n = ts_min(stk_low, n)
        high_n = ts_max(stk_high, n)
        a = high_n - low_n
        a[abs(a)<1e-8] = np.nan
        stochastics = (stk_close- low_n) / a
        stochastics_low = ts_min(stochastics, m)
        stochastics_high = ts_max(stochastics, m)
        c = stochastics_high - stochastics_low
        c[abs(c)<1e-8] = np.nan
        stochastics_double = (stochastics - stochastics_low) / c
        factor_init = stochastics_double
        
        factor_raw = (factor_init * volatility_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 40)
        factor = ts_rank(factor_mean, 240*2)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator import FactorGenerator
from operators_wyc import *

class wyc_ts32_future_if(FactorGenerator):
    def __init__(self):

        required_columns=['close_if', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts32_future_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        temp = df['close_if'].copy()
        N = 20
        UP = temp.copy(deep=True)
        UP[df['close_if'] > delay(df['close_if'], 1)] = std(df['close_if'], N)
        UP[df['close_if'] <= delay(df['close_if'], 1)] = 0
        factor = sma(UP, 40, 1)
        factor = ts_rank(factor, 100)
        factor = ts_mean(factor, 10)
        mask = df['recent_month_mask']
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor[factor >= 0.5] = 0
        
        return factor
##########
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator


def log(df):
    return np.log(df[df > 0])


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


class wsc1_future_if(FactorGenerator):
    def __init__(self):
        required_columns = ['close_if', 'recent_month_mask']
        lookback_bars = 2000
        super(wsc1_future_if, self).__init__(required_columns=required_columns,
                                              lookback_bars=lookback_bars)

    def on_bar(self, df):
        # 算法搜索
        mask = df['recent_month_mask']
        factor = log(df['close_if'])
        factor = rolling_norm(factor)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor <= -0.5] = 0
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 10:07:50 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class hhll_ind_nr_as_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_hs300', 'weight_boolean_hs300', 'high_hs300', 'low_hs300']

        super(hhll_ind_nr_as_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, data):
        df_s = (data['amount_hs300'].rolling(120, min_periods = 15).sum())[data['weight_boolean_hs300']]
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        mask = stk_amount
        temp1 = (data['high_hs300']>data['high_hs300'].shift(1)).astype(int)
        temp2 = (data['low_hs300']>data['low_hs300'].shift(1)).astype(int)
        
        temp =  temp1+temp2
        temp[temp==2] = 4
        temp = rolling_norm(temp, 242*5)
        tempdf = (temp*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(60, min_periods = 30).mean()
        factor = ts_rank(factor, 2400)
        factor.columns = [self.__class__.__name__]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 18:19:29 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class GA_ind_nr_tr_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['high_hs300','open_hs300', 'low_hs300', 'weight_boolean_hs300', 'close_hs300', 'turnover_hs300']

        super(GA_ind_nr_tr_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, data):
        turnover = (data['turnover_hs300'].rolling(60, min_periods = 15).mean())[data['weight_boolean_hs300']]
        turnover_rank = 2 * turnover.rank(axis=1, pct=True) - 1
        mask = turnover_rank
        a = data['high_hs300'].rolling(120, min_periods = 60).max()-data['open_hs300'].shift(120)
        b = data['close_hs300'] - data['low_hs300'].rolling(120, min_periods = 60).min()
        c = (data['high_hs300'].rolling(120, min_periods = 60).max()-data['low_hs300'].rolling(120, min_periods = 60).min())*2
        c[abs(c) < 1e-8] = np.nan
        vwtc_r = (a+b)/c
        vwtc_r = rolling_norm(vwtc_r)
        tempdf = (vwtc_r*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(5, min_periods = 2).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 09:55:30 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex

class Lma_te_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['turnover_hs300',  'low_hs300', 'turnover_hs300', 'close_hs300', 'weight_boolean_hs300']

        super(Lma_te_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

   
    def on_bar(self, df):
        turnover = (df['turnover_hs300'].rolling(60, min_periods = 15).mean())[df['weight_boolean_hs300']]
        ret_30 = (df['turnover_hs300']/df['turnover_hs300'].shift(30)-1)[df['weight_boolean_hs300']]
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)
        temp5 = ret_30.gt(pd.Series(ret_30.quantile(0.80, axis = 1)), axis=0)     
        mask = temp4*temp5
        
        vwtc_r = (df['low_hs300']-df['close_hs300'].rolling(120, min_periods = 30).mean())
        tempdf = (vwtc_r*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(8, min_periods = 2).mean()
        factor = ts_rank(factor)
        factor = factor.rolling(3, min_periods = 1).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor

##########
from factor_generator import FactorGenerator
from operators_wyc import *

class wyc_ts38_spot_if(FactorGenerator):
    def __init__(self):

        required_columns=['close_spot_if']
        lookback_bars=2000
        super(wyc_ts38_spot_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        smaM = 50
        stdN = 10
        temp1 = df['close_spot_if'].copy()
        temp1[df['close_spot_if'] > delay(df['close_spot_if'], 1)] = std(df['close_spot_if'], stdN)
        temp1[df['close_spot_if'] <= delay(df['close_spot_if'], 1)] = 0
        a = sma(temp1, smaM, 1)
        temp1[df['close_spot_if'] > delay(df['close_spot_if'], 1)] = 0
        temp1[df['close_spot_if'] <= delay(df['close_spot_if'], 1)] = std(df['close_spot_if'], stdN)
        b = sma(temp1, smaM, 1)
        c = a + b
        c[abs(c) < 1e-8] = np.nan
        factor = a / c * 100
        factor = ts_rank_bk(factor, 120)
        factor = ts_mean(factor, 5)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 16 14:03:11 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class VolumeVol_nr_ct_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['turnover_hs300', 'stk_index_corr_hs300', 'weight_boolean_hs300', 'volume_hs300']
        super(VolumeVol_nr_ct_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa
    
    def ts_std(self, df1, d):
        # moving time-series rank for the past d periods
        if isinstance(df1, pd.DataFrame):
            output = pd.DataFrame(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                                  index=df1.index, columns=df1.columns)
        elif isinstance(df1, pd.Series):
            output = pd.Series(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                               index=df1.index, name=df1.name)
        return output
    
    def on_bar(self, data):
        
        turnover = (data['turnover_hs300'].rolling(60, min_periods = 15).mean())[data['weight_boolean_hs300']]
        stk_index_corr = data['stk_index_corr_hs300']
        temp2 = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.80, axis = 1)), axis=0)
        temp3 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0) 
        mask = temp2 * temp3
        
        vstd2_r = data['volume_hs300'].rolling(30, min_periods = 20).std()
        vstd2_r = self.normalization(vstd2_r)
        vstd2_r[np.abs(vstd2_r)>1] = np.nan
        tempdf = (vstd2_r*mask)
        tempdf = tempdf.mean(axis = 1).to_frame()
        factor = tempdf.rolling(10, min_periods = 5).mean()
        factor = self.ts_rank(factor)
        
        factor.columns = [self.__class__.__name__]
        return factor

##########
from factor_generator import FactorGenerator
import pandas as pd
import numpy as np
import bottleneck as bk


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
class ss1_zf_if(FactorGenerator):
    def __init__(self):
        required_columns = ['close_spot_if', 'high_spot_if']
        super(ss1_zf_if, self).__init__(required_columns=required_columns)

    def on_bar(self, data):
        rtn = data['close_spot_if'] / data['close_spot_if'].shift(5) - 1
        vol = rtn.rolling(250, min_periods=30).std()
        vol[vol < 1e-8] = np.nan
        ret = data['close_spot_if'] / (data['high_spot_if'].shift(5).rolling(250, min_periods=30).max()) - 1
        sig = ret / vol
        sig = ts_rank(sig, 242 * 5)
        sig = rolling_norm(sig, 242 * 5)
        sig[sig <= -0.5] = 0
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    return rolling_table


def reg_beta(df1, d):
    # 过去d期A对1:d回归的回归系数
    output = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
    for i in df1.columns:
        temp_y = df1[i].values
        temp_y = rolling_window(temp_y, d)
        temp_x = np.tile(np.arange(d) + 1, (temp_y.shape[0], 1))
        y = np.nansum((temp_y.T - np.nanmean(temp_y, axis=1).T) * (temp_x.T - np.nanmean(temp_x, axis=1).T), axis=0)
        x = np.nansum((temp_x.T - np.nanmean(temp_x, axis=1).T) ** 2, axis=0)
        flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
        flag = np.where(flag <= d - int(d / 2), 1, np.nan)
        output[i].iloc[d - 1:] = (y / x) * flag
    return output


class wsc_search1_long_if(FactorGenerator):
    def __init__(self):
        super(wsc_search1_long_if, self).__init__(required_columns=['close_spot'],
                                                  lookback_bars=2000)

    def on_bar(self, data):
        # 算法搜索
        data = data['close_spot'].to_frame()
        factor = reg_beta(data, 40)

        # factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = rolling_norm(factor, 1000)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        factor[factor<=-0.5] = 0
        #factor[factor>=0.5] = np.nan
        return factor


##########
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 16:15:39 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class cmh_ind_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns =['high_spot_if', 'close_spot_if', 'recent_month_mask']
        
        super(cmh_ind_CC_IF, self).__init__(
                                  required_columns=required_columns)

    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa

    def on_bar(self, data):

        vwtc_r = (data['high_spot_if']-data['close_spot_if'].rolling(120, min_periods = 30).mean())
        factor = vwtc_r.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor, 2420)
        factor[factor<=-0.5] = 0
        return factor

##########
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np
from utils_zsj import *


class high_low_diff_stk2idx_zsj_if(FactorGeneratorComplex):
    def __init__(self):
        super(high_low_diff_stk2idx_zsj_if, self).__init__(
            required_columns=['close_hs300', 'amount_hs300', 'high_hs300', 'low_hs300', 'open_hs300', 'weight_boolean_hs300'],
            lookback_bars=3000)

    def on_bar(self, data):
        ## prep data
        stk_close = data['close_hs300']
        stk_high = data['high_hs300']
        stk_low = data['low_hs300']
        stk_open = data['open_hs300']
        stk_amount = data['amount_hs300']
        bool_mask = data['weight_boolean_hs300']

        # factor logic
        # factor_name = 'high_low_diff_stk2idx'
        roll_win = 45
        ma_win = 15
        ts_pct_win = 3000
        min_pct = 0.9
        min_periods = int(0.5 * roll_win)
        high_open_diff = stk_high - stk_open
        open_low_diff = stk_open - stk_low
        high_low_diff_stk = high_open_diff.rolling(roll_win, min_periods).sum() - open_low_diff.rolling(roll_win,
                                                                                                        min_periods).sum()
        high_low_diff_stk2idx_raw = high_low_diff_stk[bool_mask].mean(axis=1)
        high_low_diff_stk2idx = calc_ma_helper(high_low_diff_stk2idx_raw, ma_win, ts_pct_win, min_pct)

        factor = high_low_diff_stk2idx.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc1_cfg_ar_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc1_cfg_ar_if, self).__init__(required_columns=['close_hs300', 'close_spot_if', 'weight_boolean_hs300', 'amount_hs300'],
                                             lookback_bars=2000)

    def on_bar(self, data):
        # mask
        bool_mask = data['weight_boolean_hs300']
        amount_mask = data['amount_hs300'][bool_mask]
        amount_rank_mask = 2 * amount_mask.rank(axis=1, pct=True) - 1

        # 比较过去一段时间成分股和指数收益率大小，统计那一分钟涨幅小于指数的成分股平均交易额打分
        index_return = data['close_spot_if'].pct_change(periods=60, fill_method=None)
        stock_return = data['close_hs300'].pct_change(periods=60, fill_method=None)
        excess_return = (stock_return.subtract(index_return, axis=0))
        excess_return_weight = -amount_rank_mask[excess_return < 0].mean(axis=1)
        excess_return_weight = ts_mean(excess_return_weight, 15)
        factor = ts_rank(excess_return_weight, 600)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:45:03 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *

class BS_Main2_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_300', 'weight_300', 'BuyUniqueOrderNum_300', 'SellUniqueOrderNum_300', 'close_300']
        super(BS_Main2_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    def on_bar(self, data):
        df_s = data['amount_300'].rolling(10, min_periods = 5).sum()
        df_s = df_s[data['weight_300']>0]
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)

        factor = (data['SellUniqueOrderNum_300']+data['BuyUniqueOrderNum_300']).rolling(40, min_periods = 1).sum()*(data['close_300']/data['close_300'].shift(40)-1)
        factor = (factor[bool_df]).mean(axis = 1)
        factor = factor.rolling(2, min_periods = 1).sum()
        factor = ts_rank(factor.to_frame())
        factor.columns = [self.__class__.__name__]
        factor[factor<-0] = 0
        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np


class xdy_ts13_spot_if(FactorGenerator):
    def __init__(self):
        required_columns = ['high_spot_if']
        lookback_bars = 2000
        super(xdy_ts13_spot_if, self).__init__(required_columns=required_columns,
                                               lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        high = df['high_spot_if']
        factor = ts_max(delta(rolling_normalize(ts_max(high, 121), 4 * 242), 15), 25)
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        factor.loc[factor[columnname] <= -0.5] = 0

        return factor

##########
from factor_generator import FactorGenerator
# from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk


def ts_mean(df1, d):
    # moving time-series average for the past d periods
    output = pd.DataFrame(bk.move_mean(df1, window=d, min_count=int(d / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


def ts_sum(df1, d):
    # moving time-series average for the past d periods
    output = pd.DataFrame(bk.move_mean(df1, window=d, min_count=int(d / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


def delay(df1, d):
    # A_(i-d)
    output = df1.shift(periods=d)
    return output


def rolling_normalize(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal
        

class wyc_ts28_icfuture_if(FactorGenerator):
    def __init__(self):
        required_columns = ['close', 'recent_month_mask']
        lookback_bars = 2000
        super(wyc_ts28_icfuture_if, self).__init__(
            required_columns=required_columns,
            lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        mask = df['recent_month_mask']
        M = 8
        con1 = df['close'] > delay(df['close'], M)
        factor = ts_sum(con1, M) / M * 100
        factor = ts_mean(factor, 30)
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 900)
        factor = factor[mask].sum(axis=1).to_frame()

        factor.columns = [columnname]
        factor[factor <= -0.5] = 0
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 14:44:18 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
from factor_generator import FactorGenerator


# 多头因子
class td_CC_ICIF_IF(FactorGenerator):
    def __init__(self):
        required_columns = ['low', 'high', 'recent_month_mask']

        super(td_CC_ICIF_IF, self).__init__(
            required_columns=required_columns)

    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa
    
    def on_bar(self, data):

        temp = data['low'].rolling(10, min_periods=5).min() - data['low'].rolling(60, min_periods=5).min() + data[
            'high'].rolling(10, min_periods=5).max() - data['high'].rolling(60, min_periods=5).max()

        factor = temp[data['recent_month_mask']].mean(axis = 1).to_frame()

        factor.columns = [self.__class__.__name__]
        factor = self.normalization(factor, 242*3)
        factor[factor <= -0.5] = 0
        factor[factor > 1] = 0

        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc13_cfg_vr_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc13_cfg_vr_if, self).__init__(required_columns=['close_hs300', 'open_hs300', 'stk_volatility_hs300', 'high_hs300', 'low_hs300'],
                                              lookback_bars=2000)

    def on_bar(self, data):
        # mask
        volatility_mask = data['stk_volatility_hs300']
        volatility_rank_mask = 2 * volatility_mask.rank(axis=1, pct=True) - 1

        # 东方金工20200421，通过股价在回滚区间内的位置衡量股票日内买卖压力
        stk_close = data['close_hs300']
        stk_high = data['high_hs300']
        stk_low = data['low_hs300']
        stk_open = data['open_hs300']
        stk_price = (stk_high + stk_low + stk_open + stk_close) / 4
        n = 45
        rpp = ts_sum(stk_price, n)
        high_n = ts_max(stk_high, n)
        low_n = ts_min(stk_low, n)
        temp = high_n - low_n
        temp[abs(temp)<1e-8] = np.nan
        arpp = (rpp - low_n) / temp
        factor_init = arpp

        factor_raw = (factor_init * volatility_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 2)
        factor = ts_rank(factor_mean, 240*2)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import numpy as np

class xdy_ts1_spot_tr_if(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_hs300'
        required_columns=['high' + suffix, 'close' + suffix,'turnover' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(xdy_ts1_spot_tr_if, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_hs300'
        columnname = self.__class__.__name__

        high = df['high' + suffix]
        close = df['close' + suffix]
        high[abs(high) < 1e-8] = np.nan
        gain_high_60 = high / high.shift(60) - 1
        h_c = close / high - 1
        a = ts_mean(h_c, 60)
        a[abs(a) < 1e-8] = np.nan
        factor = ts_sum(gain_high_60 / a, 10)
        factor = ts_mean(factor, 10) * -1

        t = df['turnover' + suffix][df['weight_boolean' + suffix]]
        tr = (2 * t.rank(axis=1, pct=True) - 1)
        factor = factor * tr
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 300)
        factor = ts_mean(factor, 5)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]


        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 16 13:26:44 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class LminLmean_nr_cv_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['stk_index_corr_hs300', 'weight_boolean_hs300', 'close_hs300', 'low_hs300']
        super(LminLmean_nr_cv_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa
    
    def ts_std(self, df1, d):
        # moving time-series rank for the past d periods
        if isinstance(df1, pd.DataFrame):
            output = pd.DataFrame(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                                  index=df1.index, columns=df1.columns)
        elif isinstance(df1, pd.Series):
            output = pd.Series(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                               index=df1.index, name=df1.name)
        return output
    
    def on_bar(self, df):
        stk_index_corr = df['stk_index_corr_hs300']
        stk_close = df['close_hs300']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = self.ts_std(stk_ret, 30)
        stk_volatility = stk_volatility[df['weight_boolean_hs300']]
        temp2 = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.80, axis = 1)), axis=0)
        temp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0)    
        mask = temp2 * temp3
        
        ctl_r = -df['low_hs300'].rolling(60, min_periods =15).min()/df['low_hs300'].rolling(30, min_periods =10).mean()
        ctl_r = self.normalization(ctl_r, 242*5)
        ctl_r[np.abs(ctl_r)>1] = np.nan
        tempdf = (ctl_r*mask)
        tempdf = tempdf.mean(axis = 1).to_frame()
        factor = tempdf.rolling(5, min_periods = 2).mean()
        factor = self.ts_rank(factor, 720)
        
        factor.columns = [self.__class__.__name__]
        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc20_cfg_ar_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc20_cfg_ar_if, self).__init__(required_columns=['close_hs300', 'amount_hs300', 'weight_boolean_hs300'],
                                            lookback_bars=4000)

    def on_bar(self, data):
        # mask
        stk_amount = data['amount_hs300']
        bool_mask = data['weight_boolean_hs300']
        amount_mask = stk_amount[bool_mask]
        amount_rank_mask = 2 * amount_mask.rank(axis=1, pct=True) - 1

        # 长江金工高频因子八，偏度因子
        # 计算close的偏度，偏度＞0时，大于价格均值的价格比小于价格均值的价格少，个股成交集中在价格相对较低的水平，反之亦然，因此认为偏度越小的股票未来价格更可能上升。
        # 取当分钟rolling_skew前50%的股票，计算它们的过去一分钟return，作为因子值，再套相应的mask，因为每期选出的票都不一样，所以为了时序上可比，要做一定的归一化处理。
        stk_close = data['close_hs300']
        stk_ret = ts_pct_change(stk_close, 1)[bool_mask]
        stk_skew = ts_skew(stk_close, 30)[bool_mask]
        skew_long = stk_skew.gt(stk_skew.quantile(0.5, axis=1), axis=0)
        factor_init = stk_ret[skew_long]

        factor_raw = (factor_init * stk_amount).sum(axis=1) / (stk_amount * skew_long).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 55)
        factor = rolling_norm(factor_mean, 240*5)
        
        factor = factor.to_frame() 
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor <= 0] = 0
        #factor[factor>=0.5] = np.nan
        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc22_cfg_search_as_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc22_cfg_search_as_if, self).__init__(required_columns=['open_hs300', 'amount_hs300', 'weight_boolean_hs300'],
                                                     lookback_bars=3000)

    def on_bar(self, data):
        # mask
        stk_amount = data['amount_hs300']
        bool_mask = data['weight_boolean_hs300']
        amount_mask = stk_amount[bool_mask]

        # 算子搜索
        stk_open = data['open_hs300']
        a = ts_delta(stk_open, 25)
        factor_init = ts_median(a, 25)
        factor_raw = (factor_init * amount_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 5)
        factor = ts_rank(factor_mean, 240*10)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor<=0] = 0
        return factor

##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts12_icspot_if(FactorGenerator):
    def __init__(self):
        required_columns=['close_spot']
        lookback_bars=2000
        super(wyc_ts12_icspot_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        factor = (ts_mean(df['close_spot'], 3) + ts_mean(df['close_spot'], 6) + ts_mean(df['close_spot'], 12) + ts_mean(
            df['close_spot'], 24)) / 4
        factor = ts_rank_bk(factor, 15)
        factor = ts_mean(factor, 40)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        factor[factor < -0.9] = 0
        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts5_icfuture_if(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts5_icfuture_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        mask = df['recent_month_mask']
        N = 45
        factor = pd.DataFrame(np.where((delta((ts_sum(df['close'], N) / N), N) / delay(df['close'], N)) <= 0.05,
                                       (-1 * (df['close'] - ts_min(df['close'], N))), (-1 * delta(df['close'], 3))),
                              index=df['close'].index, columns=df['close'].columns)
        factor = ts_mean(ts_rank(-1 * factor, 1200), 15)
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor[factor <= -0.8] = 0
        return factor
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    return rolling_table


def reg_beta(df1, d):
    # 过去d期A对1:d回归的回归系数
    output = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
    for i in df1.columns:
        temp_y = df1[i].values
        temp_y = rolling_window(temp_y, d)
        temp_x = np.tile(np.arange(d) + 1, (temp_y.shape[0], 1))
        y = np.nansum((temp_y.T - np.nanmean(temp_y, axis=1).T) * (temp_x.T - np.nanmean(temp_x, axis=1).T), axis=0)
        x = np.nansum((temp_x.T - np.nanmean(temp_x, axis=1).T) ** 2, axis=0)
        flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
        flag = np.where(flag <= d - int(d / 2), 1, np.nan)
        output[i].iloc[d - 1:] = (y / x) * flag
    return output


class wsc3_future_if(FactorGenerator):
    def __init__(self):
        super(wsc3_future_if, self).__init__(required_columns=['close_if', 'recent_month_mask'],
                                             lookback_bars=2000)

    def on_bar(self, data):
        # 计算过去5分钟收益率的均值和标准差的线性组合
        mask = data['recent_month_mask']
        a = data['close_if'].pct_change(5, fill_method=None)
        b = a.rolling(24, min_periods=12).mean()
        c = a.rolling(24, min_periods=12).std()
        factor = b + 2 * c
        factor = factor.rolling(10).mean()
        factor = ts_rank(factor, 600*2)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor <= -0.5] = 0
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts26_future_if(FactorGenerator):
    def __init__(self):

        required_columns=['close_if', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts26_future_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        mask = df['recent_month_mask']
        N = 6
        N1 = 4
        N2 = 8
        MTM = df['close_if'] - delay(df['close_if'], 1)
        MTMMA = multi_processing_joblib(df=MTM, func=ts_truncated_ema, n_jobs=-1, d=1200, alpha= 1/N)
        DIF = ts_mean(delay(MTMMA, 1), N1) - ts_mean(delay(MTMMA, 1), N2)
        factor = multi_processing_joblib(df=DIF, func=ts_truncated_ema, n_jobs=-1, d=1200, alpha= 1/90)
        factor = ts_rank(factor, 2 * 242)
        factor = ts_mean(factor, 120)
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        factor.columns = [columnname]
        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import numpy as np

class xdy_ts1_spot_cr_if(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_hs300'
        required_columns=['high' + suffix, 'close' + suffix,'stk_index_corr' + suffix]
        lookback_bars=2000
        super(xdy_ts1_spot_cr_if, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_hs300'
        columnname = self.__class__.__name__

        high = df['high' + suffix]
        close = df['close' + suffix]
        high[abs(high) < 1e-8] = np.nan
        gain_high_60 = high / high.shift(60) - 1
        h_c = close / high - 1
        a = ts_mean(h_c, 60)
        a[abs(a) < 1e-8] = np.nan
        factor = ts_sum(gain_high_60 / a, 10)
        factor = ts_mean(factor, 10) * -1

        cr = (2 * df['stk_index_corr' + suffix].rank(axis=1, pct=True) - 1)
        factor = factor * cr
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 150)
        factor = ts_mean(factor, 5)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        factor[factor > 0] = 0


        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 10:13:09 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator_complex import FactorGeneratorComplex

class Crossing_Turns_tr_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['open_hs300','high_hs300','low_hs300', 'amount_hs300','volume_hs300', 'turnover_hs300', 'weight_boolean_hs300', 'close_hs300']

        super(Crossing_Turns_tr_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
        

    
    def on_bar(self, data):
        turnover = (data['turnover_hs300'].rolling(60, min_periods = 15).mean())[data['weight_boolean_hs300']]
        turnover_rank = 2 * turnover.rank(axis=1, pct=True) - 1

        temp = np.abs(pd.DataFrame(np.where(data['open_hs300']-data['close_hs300'] == 0, 0.1, data['open_hs300']-data['close_hs300'])))
        
        temp.index = data['open_hs300'].index
        temp.columns = data['open_hs300'].columns
        temp0 = (data['high_hs300'] - data['low_hs300'])
        temp1 = temp0/temp
        v1 = data['volume_hs300']
        v1[abs(v1) < 1e-8] = np.nan
        vwap = data['amount_hs300']/v1
        a = (vwap/vwap.shift(1)-1).rolling(30, min_periods = 15).sum()
        vwtc_r = (temp1*(a)).rolling(25, min_periods = 5).mean()
        
        tempdf = (vwtc_r*turnover_rank).sum(axis = 1).to_frame()
        #factor = rolling_norm(tempdf, 242*5)
        #factor[abs(factor)>1] = np.nan
        factor = tempdf.rolling(5, min_periods = 3).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk

class wyc_ts5_future_cr_if(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_hs300'
        required_columns=['volume' + suffix,'high' + suffix,'close' + suffix,'amount' + suffix,'stk_index_corr' + suffix]
        lookback_bars=2000
        super(wyc_ts5_future_cr_if, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_hs300'
        columnname = self.__class__.__name__

        N = 45
        factor = pd.DataFrame(np.where((delta((ts_sum(df['close' + suffix], N) / N), N) / delay(df['close' + suffix], N))<=0.05,(-1 * (df['close' + suffix] - ts_min(df['close' + suffix], N))),(-1 * delta(df['close' + suffix], 3))),index=df['close' + suffix].index,columns=df['close' + suffix].columns)
        factor = ts_mean(ts_rank(-1*factor, 1200),15)

        cr = (2 * df['stk_index_corr' + suffix].rank(axis=1, pct=True) - 1)
        factor = factor * cr
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]
        factor[factor < 0] = 0


        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc3_cfg_as_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc3_cfg_as_if, self).__init__(required_columns=['close_hs300', 'open_hs300', 'high_hs300', 'low_hs300', 'weight_boolean_hs300', 'amount_hs300'],
                                             lookback_bars=2000)

    def on_bar(self, data):
        # mask
        bool_mask = data['weight_boolean_hs300']
        amount_mask = data['amount_hs300'][bool_mask]

        # 用(close-open)/(high-low)衡量当下分钟的股价波动
        stk_close = data['close_hs300']
        stk_open = data['open_hs300']
        stk_high = data['high_hs300']
        stk_low = data['low_hs300']
        a = stk_high - stk_low
        a[abs(a)<1e-5] = np.nan
        b = stk_close - stk_open
        b[b<0] = np.nan
        factor_init = ts_sum(b/a, 60)
        factor_raw = (factor_init * amount_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 25)
        factor = ts_rank(factor_mean, 1800)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 13:08:25 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex

class L123_nr_wv_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['close_hs300','weight_boolean_hs300', 'low_hs300', 'turnover_hs300', 'weight_hs300']

        super(L123_nr_wv_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, df):
        stk_close = df['close_hs300']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = ts_std(stk_ret, 30)
        stk_volatility = stk_volatility[df['weight_boolean_hs300']]
        stk_weight = (df['weight_hs300'])[df['weight_boolean_hs300']]
        temp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0)        
        mask = stk_weight*temp3
        
        hlow = df['low_hs300']
        i11 = (hlow.rolling(10, min_periods = 5).min()-hlow.rolling(25, min_periods = 10).min())
        i12 = hlow.rolling(20, min_periods = 15).min()-hlow.rolling(30, min_periods = 10).min()
        i2 = (i11-i12)
        i2 = rolling_norm(i2)
        tempdf = (i2*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(60, min_periods = 30).mean()
        factor = ts_rank(factor, 2400)
        factor.columns = [self.__class__.__name__]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 15:39:28 2020

@author: appadmin
"""

import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator

class ClMaxClMin_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['close', 'recent_month_mask']
 
        super(ClMaxClMin_CC_IF, self).__init__(
                                  required_columns=required_columns)
    

        
    
        
    def on_bar(self, data):
        m_vwap_ind_r = (data['close']).rolling(40, min_periods = 30).max()/data['close'].rolling(40, min_periods = 30).min()
        factor = m_vwap_ind_r[data['recent_month_mask']].mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factor = rolling_norm(factor, 242*2)
        factor = factor.rolling(2, min_periods = 1).mean()
        factor = ts_rank(factor)
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 15:53:04 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator

class CloseVoltoMean_CC_IF_aug(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot_if']

        super(CloseVoltoMean_CC_IF_aug, self).__init__(
                                  required_columns=required_columns)

    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa
    
    def on_bar(self, data):

        prstd3_r = data['close_spot_if'].rolling(90, min_periods =10).std()/data['close_spot_if'].rolling(90, min_periods =15).mean()
        factor = prstd3_r.to_frame()

        factor.columns =  [self.__class__.__name__]
        factor = self.normalization(factor)
        factor[factor>1] = 0
        factor[factor<=-0.5] = 0
        return factor
    

##########
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 10:18:10 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

from factor_generator import FactorGenerator


class ICIF1_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns =['close', 'recent_month_mask']

        super(ICIF1_CC_IF, self).__init__(
                                  required_columns=required_columns)
        

    

    
    def on_bar(self, data):
        temp5 = data['close'].rolling(5, min_periods = 2).mean()
        temp10 = data['close'].rolling(10, min_periods = 5).mean()
        temp20 = data['close'].rolling(20, min_periods = 10).mean()
        temp60 = data['close'].rolling(60, min_periods = 30).mean()
        temp120 = data['close'].rolling(120, min_periods = 60).mean()
        temp5_diff = (temp5.diff()>0).astype(int)
        temp10_diff = (temp10.diff()>0).astype(int)
        temp20_diff = (temp20.diff()>0).astype(int)
        temp60_diff = (temp60.diff()>0).astype(int)
        temp120_diff = (temp120.diff()>0).astype(int)
        temp = (temp5_diff+temp10_diff+temp20_diff+temp60_diff+temp120_diff).rolling(15, min_periods = 5).mean()
        factor = ts_rank(temp[data['recent_month_mask']].mean(axis = 1).to_frame())
        factor.iloc[:, 0] = factor.iloc[:, 0].rolling(10, min_periods = 2).mean()
        factor.columns = [self.__class__.__name__]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 28 09:46:19 2020

@author: appadmin
"""
from factor_generator import FactorGenerator
from operators_cc import *
import pandas as pd
import numpy as np

class LRS_max_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['vwap', 'recent_month_mask']
 
        super(LRS_max_CC_IF, self).__init__(
                                  required_columns=required_columns)
        
    def on_bar(self, data):
        #448_LINEARREG_SLOPE(ts_max(twap, 40), 50)
        columnname = self.__class__.__name__
        temp1 = data['vwap'].rolling(50, min_periods = 20).max()
        holder = {}
        for item in temp1.columns:
            close_spot = (temp1[item]).values
            x = np.array(range(len(data['vwap'][item])))
            #print(item)
            holder[item] = pd.Series(rolling_linear_reg(x, close_spot, 50))

        temp = pd.DataFrame(holder)
        temp.index = data['vwap'].index
        

        temp = (temp[data['recent_month_mask']]).mean(axis = 1)
        
        cc3 = ts_rank(temp.to_frame(), 500)
        cc3.columns = [columnname]
        return cc3
##########
from factor_generator import FactorGenerator
# from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk


def ts_mean(df1, d):
    # moving time-series average for the past d periods
    output = pd.DataFrame(bk.move_mean(df1, window=d, min_count=int(d / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


def ts_sum(df1, d):
    # moving time-series average for the past d periods
    output = pd.DataFrame(bk.move_mean(df1, window=d, min_count=int(d / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


def rolling_normalize(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


class wyc_ts19_future_if(FactorGenerator):
    def __init__(self):
        required_columns = ['close_if', 'low_if', 'high_if', 'volume_if', 'recent_month_mask']
        lookback_bars = 2000
        super(wyc_ts19_future_if, self).__init__(
            required_columns=required_columns,
            lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        mask = df['recent_month_mask']
        a = (df['high_if']- df['low_if'])
        a[abs(a) < 1e-8] = np.nan
        factor = ts_sum((((df['close_if'] - df['low_if']) - (df['high_if'] - df['close_if'])) / a * df['volume_if']), 20)
        factor = ts_rank(factor, 240)
        factor = ts_mean(factor, 120)
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 1200)
        factor = factor[mask].sum(axis=1).to_frame()

        factor.columns = [columnname]
        factor[factor <= -0.5] = 0

        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 09:45:43 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class LCCorr_nr_a3_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_boolean_hs300', 'close_hs300', 'low_hs300', 'amount_hs300']

        super(LCCorr_nr_a3_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

   
    def on_bar(self, df):
        
        df_s = (df['amount_hs300'].rolling(120, min_periods = 15).sum())[df['weight_boolean_hs300']]
        ret = (df['close_hs300']/df['close_hs300'].shift(30)-1)[df['weight_boolean_hs300']]
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0)
        temp6 = ret.gt(pd.Series(ret.quantile(0.80, axis = 1)), axis=0)       
        mask = temp1*temp6
        
        high = df['low_hs300']
        close = df['close_hs300']
        s = high.rolling(60, min_periods=30).std()
        f = close.rolling(60, min_periods=30).std()
        s[abs(s) < 1e-7] = np.nan
        f[abs(f) < 1e-7] = np.nan
        t_chgpcor2 = high.rolling(60, min_periods=30).cov(close) / (s * f)
        t_chgpcor2 = rolling_norm(t_chgpcor2)
        tempdf = (t_chgpcor2*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(15, min_periods = 15).mean()
        factor = ts_rank(factor, 2400)
        factor.columns = [self.__class__.__name__]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 09:42:38 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator_complex import FactorGeneratorComplex

class RS_ind_wt_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_hs300', 'turnover_hs300', 'weight_boolean_hs300', 'close_hs300']

        super(RS_ind_wt_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
        

    
    def on_bar(self, df):
        stk_weight = (df['weight_hs300'])[df['weight_boolean_hs300']]
        turnover = (df['turnover_hs300'].rolling(60, min_periods = 15).mean())[df['weight_boolean_hs300']]
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)
        wt = stk_weight*temp4
        ret = df['close_hs300']/df['close_hs300'].shift(1)-1
        a = ret.rolling(25, min_periods = 15).std()
        a[abs(a)<1e-8] = np.nan
        i1 = (df['close_hs300']/df['close_hs300'].shift(24)-1) / a
        
        tempdf = (i1*wt).sum(axis = 1)
        factor = tempdf.rolling(8, min_periods = 4).mean().to_frame()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor
##########
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
from help_functions_wsc import multi_processing_joblib
from operators_wsc import *



class wsc8_future_if(FactorGenerator):
    def __init__(self):
        super(wsc8_future_if, self).__init__(required_columns=['close_if', 'high_if', 'low_if', 'recent_month_mask'],
                                              lookback_bars=2000)

    def on_bar(self, data):
        mask = data['recent_month_mask']
        close = data['close_if']
        high = data['high_if']
        low = data['low_if']
        n = 30
        m = 80
        low_n = ts_min(low, n)
        high_n = ts_max(high, n)
        a = high_n - low_n
        a[abs(a)<1e-8] = np.nan
        b = (close- low_n) / (high_n - low_n)
        b_low = ts_min(b, m)
        b_high = ts_max(b, m)
        c = b_high - b_low
        c[abs(c)<1e-8] = np.nan
        d = (b - b_low) / c
        e = multi_processing_joblib(d, ts_truncated_ema, n_jobs=-1, d=60, alpha=2/3)
        factor = multi_processing_joblib(e, ts_truncated_ema, n_jobs=-1, d=60, alpha=2/3)
        factor = ts_mean(factor, 140)
        factor = ts_rank(factor, 1800)
        factor = factor[mask].sum(axis=1)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        #factor[factor <= -0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc5_cfg_vs_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc5_cfg_vs_if, self).__init__(required_columns=['close_hs300', 'stk_volatility_hs300'],
                                             lookback_bars=3000)

    def on_bar(self, data):
        # mask
        volatility_mask = data['stk_volatility_hs300']
        
        # 计算长短两条均线包围的面积
        stk_close = data['close_hs300']
        ma_long = ts_mean(stk_close, 95)
        ma_short = ts_mean(stk_close, 15)
        ma_diff = ma_short - ma_long
        factor_init = ma_diff
        factor_raw = (factor_init * volatility_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 25)
        factor = ts_rank(factor_mean, 240*15)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 16:25:02 2020

@author: appadmin
"""

import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator


class SLHS_CC_ICIF_IF(FactorGenerator):
    def __init__(self):

        required_columns =['high_spot']

        super(SLHS_CC_ICIF_IF, self).__init__(
                                  required_columns=required_columns)
        


    
    def on_bar(self, data):


        high_spot = data['high_spot'].values
        
        ind = list(range(len(high_spot)))

        m_vwap_ind_r = rolling_linear_reg(ind, high_spot, 60)
        #factor = pd.Series(data['close_spot_if'].rolling(25, min_periods = 1).skew()).to_frame()
        factor = pd.Series(m_vwap_ind_r).to_frame()
        factor.index = data['high_spot'].index
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        #factor[factor>1] = np.nan
        factor[factor<=-0.5] = np.nan
        factor = ts_rank(factor, 242*6)
        factor = ts_rank(factor)
        factor[factor<=-0.5] = 0

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 10:26:32 2021

@author: appadmin
"""

from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *
import numpy as np

class BS_7_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['buy_superorder_money_300', 'buy_bigorder_money_300', 'amount_300']

        super(BS_7_CC_IF, self).__init__(required_columns=required_columns
                                  )

    def on_bar(self, data):
        factor = (data['buy_superorder_money_300']+data['buy_bigorder_money_300'])/(data['amount_300'])
        factor = factor.replace([np.inf, -np.inf], np.nan)
        
        factor = factor.rolling(20, min_periods = 2).mean()

        factor = factor.mean(axis = 1)
        factor = ts_rank(factor.to_frame())
        factor.columns = [self.__class__.__name__]

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 14:56:54 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator


class HL123_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns=['low_if', 'high_if','recent_month_mask']

        super(HL123_CC_IF, self).__init__(required_columns=required_columns)
    

    

    def on_bar(self, df):
        columnname = self.__class__.__name__
        hlow = df['low_if']
        hhigh = df['high_if']
        i11 = hhigh.rolling(10, min_periods = 5).max()-hlow.rolling(60, min_periods = 10).min()
        i12 = (hhigh.shift(30)).rolling(10, min_periods = 5).max()-(hlow.shift(30)).rolling(60, min_periods = 10).min()
        i2 = (i11-i12).rolling(20, min_periods = 2).mean()
        i2 = ts_rank(i2[df['recent_month_mask']].mean(axis = 1).to_frame())
        #i2 = rolling_norm(i2)
        i2[i2>1] = 0
        i2[i2<=-0.5] = 0
        i2.columns = [columnname]    
        return i2
##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import numpy as np

class xdy_ts6_spot_tr_if(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_hs300'
        required_columns=['close' + suffix,'turnover' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(xdy_ts6_spot_tr_if, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_hs300'
        columnname = self.__class__.__name__

        close = df['close' + suffix]
        gain_close_30 = ts_gain(close, 30)
        factor = ts_levelchange(gain_close_30, 20)
        factor = ts_mean(factor, 110)

        t = df['turnover' + suffix][df['weight_boolean' + suffix]]
        tr = (2 * t.rank(axis=1, pct=True) - 1)
        factor = factor * tr
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 300)
        factor = ts_mean(factor, 5)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        factor[factor<0] = 0

        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc6_cfg_vr_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc6_cfg_vr_if, self).__init__(required_columns=['close_hs300', 'close_spot_if', 'stk_volatility_hs300'],
                                             lookback_bars=2000)

    def on_bar(self, data):
        # mask
        volatility_mask = data['stk_volatility_hs300']
        volatility_rank_mask = 2 * volatility_mask.rank(axis=1, pct=True) - 1

        # 计算长短期收益率之差，并只保留大于0的部分
        stk_close = data['close_hs300']
        stk_ret_short = ts_pct_change(stk_close, 10)
        stk_ret_long = ts_pct_change(stk_close, 60)
        factor_init = stk_ret_long - stk_ret_short
        factor_init[factor_init<0] = 0
        factor_raw = (factor_init * volatility_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 10)
        factor = ts_rank(factor_mean, 240*2)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 15:27:40 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
import numpy as np
from factor_generator import FactorGenerator

class ZHZH_ind_ICIF_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['high_spot']

        super(ZHZH_ind_ICIF_CC_IF, self).__init__(
                                  required_columns=required_columns)

    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa
    
    def on_bar(self, data):
        temp = (data['high_spot']>=(data['high_spot'].rolling(15, min_periods = 5).max())).astype(int).rolling(60, min_periods = 5).mean()
        factor = self.ts_rank(temp.to_frame())
        #factor = self.ts_rank(factor)
        factor[factor<=-0.5] = 0
        factor.columns = [self.__class__.__name__]
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 12:49:27 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex

class LminLmean_nr_corrturn_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['turnover_hs300', 'weight_boolean_hs300', 'low_hs300','stk_index_corr_hs300']

        super(LminLmean_nr_corrturn_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, df):
        
        turnover = (df['turnover_hs300'].rolling(60, min_periods = 15).mean())[df['weight_boolean_hs300']]   
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)
        temp2 = df['stk_index_corr_hs300'].gt(pd.Series(df['stk_index_corr_hs300'].quantile(0.80, axis = 1)), axis=0)
        mask = temp4*temp2
        
        ctl_r = -df['low_hs300'].rolling(60, min_periods =15).min()/df['low_hs300'].rolling(30, min_periods =10).mean()
        lltc_ind_r = rolling_norm(ctl_r)
        tempdf = (lltc_ind_r*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(10, min_periods = 5).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    return rolling_table


def reg_beta(df1, d):
    # 过去d期A对1:d回归的回归系数
    output = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
    for i in df1.columns:
        temp_y = df1[i].values
        temp_y = rolling_window(temp_y, d)
        temp_x = np.tile(np.arange(d) + 1, (temp_y.shape[0], 1))
        y = np.nansum((temp_y.T - np.nanmean(temp_y, axis=1).T) * (temp_x.T - np.nanmean(temp_x, axis=1).T), axis=0)
        x = np.nansum((temp_x.T - np.nanmean(temp_x, axis=1).T) ** 2, axis=0)
        flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
        flag = np.where(flag <= d - int(d / 2), 1, np.nan)
        output[i].iloc[d - 1:] = (y / x) * flag
    return output


def ts_delay(df1, d):
    # A_(i-d)
    output = df1.shift(periods=d)
    return output


def ts_mean(df1, d):
    # moving time-series average for the past d periods
    output = pd.DataFrame(bk.move_mean(df1, window=d, min_count=int(d / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


class wsc4_future_kpz_if(FactorGenerator):
    def __init__(self):
        super(wsc4_future_kpz_if, self).__init__(required_columns=['close', 'recent_month_mask'],
                                                lookback_bars=2000)

    def on_bar(self, data):
        # dpo技术指标
        mask = data['recent_month_mask']
        close = data['close']
        N = 20
        dpo = close - ts_delay(ts_mean(close, N), int(N/2+1))
        factor = abs(dpo - dpo.rolling(60, min_periods=30).median())
        factor = factor.rolling(45, min_periods=10).mean()
        factor = ts_rank(factor, 600*2)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]

        # factor[factor <= -0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


class wsc_ma1_if(FactorGenerator):
    def __init__(self):
        super(wsc_ma1_if, self).__init__(required_columns=['close_if', 'recent_month_mask'],
                                         lookback_bars=2000)

    def on_bar(self, data):
        # 计算长周期和短周期两条均线，作差表示这两条均线包围的面积
        close = data['close_if']
        mask = data['recent_month_mask']
        close_ma_long = close.rolling(120, min_periods=60).mean()
        close_ma_short = close.rolling(15, min_periods=5).mean()
        factor = close_ma_short - close_ma_long
        factor = rolling_norm(factor, 360)
        factor = factor[mask].sum(axis=1)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 13:46:35 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator


class MALS_ICIF_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns=['low_spot']
        super(MALS_ICIF_CC_IF, self).__init__(required_columns=required_columns)
        

    

    
    def on_bar(self, data):

        temp = data['low_spot'].rolling(75, min_periods = 15).mean() - data['low_spot'].shift(15).rolling(60, min_periods = 7).mean()
        factor = temp.to_frame()
        factor = ts_rank(factor, 242*2)
        factor[factor<-0.5] = 0
        factor.columns = [self.__class__.__name__]
        return factor
##########
# -*- coding: utf-8 -*-
"""
author:       sujian zhi
fred:         minute
prod:         IC.CFE
factor_name:  fac
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
from utils_zsj import *

"""
import inspect, os, sys
code_base = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.dirname(code_base))
from ts.factor.minute.utils_zsj import *
"""

class kpz_ma_displaced_std_zsj_if(FactorGenerator):
    def __init__(self):
        super(kpz_ma_displaced_std_zsj_if, self).__init__(required_columns = ['close', 'recent_month_mask'],
                                                   lookback_bars = 1500)

    def on_bar(self, data):
        ##### def data #####
        close = data['close']
        mask = data['recent_month_mask']

        ##### calc factor #####

        def calc_ma_displaced(close, short_win=10, long_win=20):
            ma_close = MA(close, long_win)
            ma_displaced = REF(ma_close, short_win)
            ma_diff = close - ma_displaced
            return ma_diff

        factor_name = 'ma_displaced_std'
        short_win = 10
        long_win = 90
        std_win = 40
        ts_pct_win = 242*5
        score_raw = calc_ma_displaced(close, short_win, long_win)
        ma_displaced_std = calc_std_helper(score_raw, std_win, ts_pct_win)
        ma_displaced_std = ma_displaced_std[mask].sum(axis=1)

        ##### format factor #####
        ma_displaced_std.name = self.__class__.__name__
        factor = pd.DataFrame(ma_displaced_std) 
        return factor

##########
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np


def place_back_format(dat_mat, dat_orig):
    if isinstance(dat_orig, pd.DataFrame):
        dat_fmt = pd.DataFrame(dat_mat, index=dat_orig.index, columns=dat_orig.columns)
    elif isinstance(dat_orig, pd.Series):
        dat_fmt = pd.Series(dat_mat, index=dat_orig.index)
        dat_fmt.name = dat_orig.name
    else:
        dat_fmt = dat_mat
    return dat_fmt


def calc_ts_pct(ts_dat, roll_win=20, min_pct=1, force_range=False):
    min_win = int(min_pct * roll_win)
    ts_dat_pct_np = bk.move_rank(ts_dat, window=roll_win, min_count=min_win, axis=0)
    if force_range:
        ts_dat_pct_np = (ts_dat_pct_np + 1) / 2
    ts_dat_pct = place_back_format(ts_dat_pct_np, ts_dat)
    return ts_dat_pct


def calc_change_helper(score_raw, short_win, long_win, ts_pct_win, sign=1, min_pct=0.9):
    score_change_raw = sign * (
            score_raw.rolling(short_win, int(min_pct * short_win)).mean() - score_raw.rolling(long_win, int(
        min_pct * long_win)).mean())
    score_change = calc_ts_pct(score_change_raw, ts_pct_win, min_pct=min_pct)
    return score_change


def calc_std_helper(score_raw, std_win, ts_pct_win, min_pct=0.9):
    score_std_raw = score_raw.rolling(std_win, int(min_pct * std_win)).std()
    score_std = calc_ts_pct(score_std_raw, ts_pct_win)
    return score_std


def calc_ma_helper(score_raw, ma_win, ts_pct_win, min_pct=0.9):
    score_ma_raw = score_raw.rolling(ma_win, int(min_pct * ma_win)).mean()
    score_ma = calc_ts_pct(score_ma_raw, ts_pct_win, min_pct=min_pct)
    return score_ma


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


class high_low_diff_a2p_zsj_if(FactorGeneratorComplex):
    def __init__(self):
        super(high_low_diff_a2p_zsj_if, self).__init__(
            required_columns=['close_hs300', 'amount_hs300', 'high_hs300', 'low_hs300', 'open_hs300', 'weight_boolean_hs300'],
            lookback_bars=3000)

    def on_bar(self, data):
        ## prep data
        stk_close = data['close_hs300']
        stk_high = data['high_hs300']
        stk_low = data['low_hs300']
        stk_open = data['open_hs300']
        stk_amount = data['amount_hs300']
        bool_mask = data['weight_boolean_hs300']

        amount_mask = stk_amount[bool_mask]
        cut_line = amount_mask.median(axis=1)
        active_mask = amount_mask.subtract(cut_line, axis=0) >= 0
        inactive_mask = amount_mask.subtract(cut_line, axis=0) < 0

        # factor logic
        # factor_name = 'high_low_diff_a2p'
        roll_win = 45
        ma_win = 45
        ts_pct_win = 2400
        min_pct = 0.9
        min_periods = int(roll_win * min_pct)
        high_open_diff = stk_high - stk_open
        open_low_diff = stk_open - stk_low
        high_low_diff_stk = high_open_diff.rolling(roll_win, min_periods).sum() - \
                            open_low_diff.rolling(roll_win, min_periods).sum()
        high_low_diff_active_raw = high_low_diff_stk[active_mask].mean(axis=1)
        high_low_diff_inactive_raw = high_low_diff_stk[inactive_mask].mean(axis=1)
        high_low_diff_a2p_raw = high_low_diff_active_raw - high_low_diff_inactive_raw
        high_low_diff_a2p = calc_ma_helper(high_low_diff_a2p_raw, ma_win, ts_pct_win, min_pct)

        factor = high_low_diff_a2p.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor<=0] = 0
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 17:17:34 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator

class LminLmean_CC_ICIF_IF(FactorGenerator):
    def __init__(self):
        required_columns =['low', 'recent_month_mask']
        super(LminLmean_CC_ICIF_IF, self).__init__(
                                  required_columns=required_columns)
    

    
    def on_bar(self, data):

        ctl_r = -data['low'].rolling(60, min_periods =15).min()/data['low'].rolling(30, min_periods =10).mean()
        factor = ctl_r[data['recent_month_mask']].mean(axis = 1).to_frame()

        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        #factor[factor<=-0.5] = np.nan
        return factor
##########
# -*- coding: utf-8 -*-
"""
author:       sujian zhi
fred:         minute
prod:         IC.CFE
factor_name:  fac
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
from utils_zsj import *

"""
import inspect, os, sys
code_base = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.dirname(code_base))
from ts.factor.minute.utils_zsj import *
"""


class kpz_dpo_std_zsj_if(FactorGenerator):
    def __init__(self):
        super(kpz_dpo_std_zsj_if, self).__init__(factor_name='dpo_std_zsj',
                                                 required_columns=['close', 'recent_month_mask'],
                                                 lookback_bars=1500)

    def on_bar(self, data):
        ##### def data #####
        close = data['close']
        mask = data['recent_month_mask']

        ##### calc factor #####

        def calc_dpo_sig(close, roll_win):
            dpo = close - REF(MA(close, roll_win), int(roll_win / 2 + 1))
            return dpo

        dpo_win = 45
        ma_win = 30
        ts_pct_win = 1200
        dpo_raw = calc_dpo_sig(close, dpo_win)
        dpo_std_raw = dpo_raw.rolling(ma_win, 1).std()
        dpo_std = calc_ts_pct(dpo_std_raw, ts_pct_win)
        dpo_std = dpo_std[mask].sum(axis=1)

        ##### format factor #####
        dpo_std.name = self.__class__.__name__
        factor = pd.DataFrame(dpo_std)
        factor[factor <= -0.5] = 0
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 15:13:20 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator

class Rev_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['close_if', 'recent_month_mask']

        super(Rev_CC_IF, self).__init__(
                                  required_columns=required_columns)

    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa

    def on_bar(self, data):

        vwtc_r = data['close_if']/data['close_if'].shift(120)-1
        factor = vwtc_r.rolling(3, min_periods = 2).mean()[data['recent_month_mask']].mean(axis = 1).to_frame()
  
        factor.columns = [self.__class__.__name__]
        factor = self.normalization(factor, 242*8)
        factor[factor<-1] = 0
        factor[factor>1] = 0
        return factor


##########
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 16 13:50:40 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex

class td_cv_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['stk_index_corr_hs300', 'weight_boolean_hs300', 'close_hs300', 'low_hs300', 'high_hs300']
        super(td_cv_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, data):
        stk_close = data['close_hs300']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = ts_std(stk_ret, 30)
        stk_volatility = stk_volatility[data['weight_boolean_hs300']]
        stk_index_corr = data['stk_index_corr_hs300']
        temp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0)
        temp2 = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.80, axis = 1)), axis=0) 
        mask = temp2 * temp3
        
        temp = data['low_hs300'].rolling(10, min_periods = 5).min()-data['low_hs300'].rolling(60, min_periods = 5).min()+data['high_hs300'].rolling(10, min_periods = 5).max()-data['high_hs300'].rolling(60, min_periods = 5).max()

        tempdf = (temp*mask)
        tempdf = tempdf.mean(axis = 1).to_frame()
        factor = tempdf.rolling(15, min_periods = 7).mean()
        factor = ts_rank(factor, 720)
        
        factor.columns = [self.__class__.__name__]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 09:39:52 2020

@author: appadmin
"""

import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex

class L123_at_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_boolean_hs300',  'low_hs300', 'turnover_hs300', 'amount_hs300']

        super(L123_at_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, df):
        
        df_s = (df['amount_hs300'].rolling(120, min_periods = 15).sum())[df['weight_boolean_hs300']]
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0)
        turnover = (df['turnover_hs300'].rolling(60, min_periods = 15).mean())[df['weight_boolean_hs300']]
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)        
        mask = temp1*temp4
        
        hlow = df['low_hs300']
        i11 = (hlow.rolling(10, min_periods = 5).min()-hlow.rolling(25, min_periods = 10).min())
        i12 = hlow.rolling(20, min_periods = 15).min()-hlow.rolling(30, min_periods = 10).min()
        i2 = (i11-i12)
        tempdf = (i2*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(30, min_periods = 15).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor
##########
