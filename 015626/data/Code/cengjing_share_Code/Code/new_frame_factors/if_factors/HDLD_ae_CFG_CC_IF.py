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