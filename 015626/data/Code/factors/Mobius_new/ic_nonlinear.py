# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 10:26:42 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class BidAskAmtRatio_Weighted(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['Bid1AmtMean', 'Ask1AmtMean', 'weight']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        a = data['Bid1AmtMean'].iloc[-1] 
        b = data['Ask1AmtMean'].iloc[-1]
        w = data['weight'].iloc[-1].values
        a.fillna(0, inplace = True)
        b.fillna(0, inplace = True)
        a = a.values
        b = b.values
        factor = cross(a/b)       
        
        return np.nanmean(factor*w)
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 09:36:27 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class MidOrderRatioSellMoney_Weighted_5(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['sell_superorder_money', 'sell_bigorder_money', 'sell_midorder_money', 'sell_smallorder_money', 'weight']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        sup = data['sell_superorder_money'].iloc[-240:]
        big = data['sell_bigorder_money'].iloc[-240:]
        mid = data['sell_midorder_money'].iloc[-240:]
        small = data['sell_smallorder_money'].iloc[-240:]
        
        sup.fillna(0, inplace = True)
        big.fillna(0, inplace = True)
        mid.fillna(0, inplace = True)
        small.fillna(0, inplace = True)
        
        date = str(data['sell_midorder_money'].index.date[-1]) 
        sup = sup.loc[date]
        big = big.loc[date]
        mid = mid.loc[date]
        small = small.loc[date]
        if len(big)<=5:
            if len(big) == 1:
                sup = sup.values
                big = big.values
                mid = mid.values
                small = small.values
            else:
                sup = np.nanmean(sup.values, axis = 0)
                big = np.nanmean(big.values, axis = 0)
                mid = np.nanmean(mid.values, axis = 0)
                small = np.nanmean(small.values, axis = 0)
        else:
            sup = np.nanmean(sup.iloc[-5:].values, axis = 0)
            big = np.nanmean(big.iloc[-5:].values, axis = 0)
            mid = np.nanmean(mid.iloc[-5:].values, axis = 0)
            small = np.nanmean(small.iloc[-5:].values, axis = 0)

        temp = cross4(sup+big+mid+small)
        
        factor = np.nanmean(data['weight'].iloc[-1].values * mid/temp)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 16:16:11 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd



class BigOrderRatioBuyMoney_Weighted(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['buy_superorder_money', 'buy_bigorder_money', 'buy_midorder_money', 'buy_smallorder_money', 'weight']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        sup = data['buy_superorder_money'].iloc[-1]
        big = data['buy_bigorder_money'].iloc[-1]
        mid = data['buy_midorder_money'].iloc[-1]
        small = data['buy_smallorder_money'].iloc[-1]
        weight = data['weight'].iloc[-1].values
        
        sup.fillna(0, inplace = True)
        big.fillna(0, inplace = True)
        mid.fillna(0, inplace = True)
        small.fillna(0, inplace = True)
        
        temp = cross4(sup.values+big.values + mid.values + small.values)
        
        factor = np.nanmean(weight * big/temp)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 13:52:51 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class position(FutureFactor):

    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IC':['OpenInterest']} 
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    

    def calculate(self, data):
        factor = data['OpenInterest_cont_IC'].iloc[-1]
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 14:54:36 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class turnover_mean(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['turnover_rate']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        factor = np.nanmean(data['turnover_rate'].iloc[-1])
        
        return np.nanmean(factor)
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 17:56:21 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class IndexCorr(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['stk_index_corr_zz500']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        factor = np.nanmean(data['stk_index_corr_zz500'].iloc[-1])
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 10:06:16 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class OFI(FutureFactor):

    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IC':['OrderFlowImbalanceLv1']} 
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    

    def calculate(self, data):
        factor = data['OrderFlowImbalanceLv1_cont_IC'].iloc[-1]


        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 11:13:34 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class SuperOrderRatioBuyMoney(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['buy_superorder_money', 'buy_bigorder_money', 'buy_midorder_money', 'buy_smallorder_money', 'weight']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        sup = data['buy_superorder_money'].iloc[-1]
        big = data['buy_bigorder_money'].iloc[-1]
        mid = data['buy_midorder_money'].iloc[-1]
        small = data['buy_smallorder_money'].iloc[-1]
        weight = data['weight'].iloc[-1].values
        
        sup.fillna(0, inplace = True)
        big.fillna(0, inplace = True)
        mid.fillna(0, inplace = True)
        small.fillna(0, inplace = True)
        
        temp = cross4(sup.values+big.values + mid.values + small.values)
        
        factor = np.nanmean(sup/temp)
        
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 14:15:32 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class position_diff(FutureFactor):

    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IC':['OpenInterest']} 
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    

    def calculate(self, data):
        factor1 = data['OpenInterest_cont_IC'].iloc[-3:].values

        factor = factor1[-1] - factor1[-2]

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 13:07:49 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class SuperOrderRatioBuy_5(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['buy_superorder_count', 'buy_bigorder_count', 'buy_midorder_count', 'buy_smallorder_count']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        sup = data['buy_superorder_count'].iloc[-240:]
        big = data['buy_bigorder_count'].iloc[-240:]
        mid = data['buy_midorder_count'].iloc[-240:]
        small = data['buy_smallorder_count'].iloc[-240:]
        
        sup.fillna(0, inplace = True)
        big.fillna(0, inplace = True)
        mid.fillna(0, inplace = True)
        small.fillna(0, inplace = True)
        
        date = str(data['buy_midorder_count'].index.date[-1]) 
        sup = sup.loc[date]
        big = big.loc[date]
        mid = mid.loc[date]
        small = small.loc[date]
        if len(big)<=5:
            if len(big) == 1:
                sup = sup.values
                big = big.values
                mid = mid.values
                small = small.values
            else:
                sup = np.nanmean(sup.values, axis = 0)
                big = np.nanmean(big.values, axis = 0)
                mid = np.nanmean(mid.values, axis = 0)
                small = np.nanmean(small.values, axis = 0)
        else:
            sup = np.nanmean(sup.iloc[-5:].values, axis = 0)
            big = np.nanmean(big.iloc[-5:].values, axis = 0)
            mid = np.nanmean(mid.iloc[-5:].values, axis = 0)
            small = np.nanmean(small.iloc[-5:].values, axis = 0)

        temp = cross4(sup+big+mid+small)
        
        factor = np.nanmean(sup/temp)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 14:47:05 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class sjx(FutureFactor):

    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IC':['close']} 
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    

    def calculate(self, data):
        hclose = data['close_cont_IC'].iloc[-121:].values
        factor = np.nanmean(hclose[-5:]) - np.nanmean(hclose[-120:])

        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 10:56:32 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class SuperOrderRatioBuyMoney_5(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['buy_superorder_money', 'buy_bigorder_money', 'buy_midorder_money', 'buy_smallorder_money', 'weight']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        sup = data['buy_superorder_money'].iloc[-240:]
        big = data['buy_bigorder_money'].iloc[-240:]
        mid = data['buy_midorder_money'].iloc[-240:]
        small = data['buy_smallorder_money'].iloc[-240:]
        
        sup.fillna(0, inplace = True)
        big.fillna(0, inplace = True)
        mid.fillna(0, inplace = True)
        small.fillna(0, inplace = True)
        
        date = str(data['buy_superorder_money'].index.date[-1]) 
        sup = sup.loc[date]
        big = big.loc[date]
        mid = mid.loc[date]
        small = small.loc[date]
        if len(big)<=5:
            if len(big) == 1:
                sup = sup.values
                big = big.values
                mid = mid.values
                small = small.values
            else:
                sup = np.nanmean(sup.values, axis = 0)
                big = np.nanmean(big.values, axis = 0)
                mid = np.nanmean(mid.values, axis = 0)
                small = np.nanmean(small.values, axis = 0)
        else:
            sup = np.nanmean(sup.iloc[-5:].values, axis = 0)
            big = np.nanmean(big.iloc[-5:].values, axis = 0)
            mid = np.nanmean(mid.iloc[-5:].values, axis = 0)
            small = np.nanmean(small.iloc[-5:].values, axis = 0)

        temp = cross4(sup+big+mid+small)
        
        factor = np.nanmean(sup/temp)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 13:25:27 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class SuperOrderRatioBuy(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['buy_superorder_count', 'buy_bigorder_count', 'buy_midorder_count', 'buy_smallorder_count']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        sup = data['buy_superorder_count'].iloc[-1]
        big = data['buy_bigorder_count'].iloc[-1]
        mid = data['buy_midorder_count'].iloc[-1]
        small = data['buy_smallorder_count'].iloc[-1]
        
        sup.fillna(0, inplace = True)
        big.fillna(0, inplace = True)
        mid.fillna(0, inplace = True)
        small.fillna(0, inplace = True)
        
        temp = cross4(sup.values+big.values + mid.values + small.values)
        
        factor = np.nanmean(sup/temp)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 09:50:03 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class MidOrderRatioSell_Weighted_5(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['sell_superorder_count', 'sell_bigorder_count', 'sell_midorder_count', 'sell_smallorder_count', 'weight']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        sup = data['sell_superorder_count'].iloc[-240:]
        big = data['sell_bigorder_count'].iloc[-240:]
        mid = data['sell_midorder_count'].iloc[-240:]
        small = data['sell_smallorder_count'].iloc[-240:]
        
        sup.fillna(0, inplace = True)
        big.fillna(0, inplace = True)
        mid.fillna(0, inplace = True)
        small.fillna(0, inplace = True)
        
        date = str(data['sell_midorder_count'].index.date[-1]) 
        sup = sup.loc[date]
        big = big.loc[date]
        mid = mid.loc[date]
        small = small.loc[date]
        if len(big)<=5:
            if len(big) == 1:
                sup = sup.values
                big = big.values
                mid = mid.values
                small = small.values
            else:
                sup = np.nanmean(sup.values, axis = 0)
                big = np.nanmean(big.values, axis = 0)
                mid = np.nanmean(mid.values, axis = 0)
                small = np.nanmean(small.values, axis = 0)
        else:
            sup = np.nanmean(sup.iloc[-5:].values, axis = 0)
            big = np.nanmean(big.iloc[-5:].values, axis = 0)
            mid = np.nanmean(mid.iloc[-5:].values, axis = 0)
            small = np.nanmean(small.iloc[-5:].values, axis = 0)

        temp = cross4(sup+big+mid+small)
        
        factor = np.nanmean(data['weight'].iloc[-1].values * mid/temp)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 11:10:19 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class SuperOrderRatioSellMoney_Weighted(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['sell_superorder_money', 'sell_bigorder_money', 'sell_midorder_money', 'sell_smallorder_money', 'weight']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        sup = data['sell_superorder_money'].iloc[-1]
        big = data['sell_bigorder_money'].iloc[-1]
        mid = data['sell_midorder_money'].iloc[-1]
        small = data['sell_smallorder_money'].iloc[-1]
        weight = data['weight'].iloc[-1].values
        
        sup.fillna(0, inplace = True)
        big.fillna(0, inplace = True)
        mid.fillna(0, inplace = True)
        small.fillna(0, inplace = True)
        
        temp = cross4(sup.values+big.values + mid.values + small.values)
        
        factor = np.nanmean(weight * sup/temp)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 13:27:39 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class Spot_Std_5(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']} 
    normalize_size = 1
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        
        hclose = data['close_000905.SH'].iloc[-6:].values
        
        factor = np.nanstd(hclose[1:] / hclose[:-1] - 1)

        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 17:17:01 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class BuyUnique_5(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'BuyTradeNum']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        a = data['BuyUniqueOrderNum'].iloc[-240:]

        date = str(a.index.date[-1])
        a1 = a.loc[date].values
        a2 = data['BuyTradeNum'].loc[date].values
        if len(a1)<=5:
            if len(a1) == 1:
                pass
            else:
                a1 = np.nanmean(a1, axis = 0)
                a2 = np.nanmean(a2, axis = 0)
        else:
            a1 = np.nanmean(a1[-5:], axis = 0)
            a2 = np.nanmean(a2[-5:], axis = 0)
            
        a2[abs(a2)<1e-8] = np.nan
        a = cross(a1/a2)

        factor = np.nanmean(a)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 18:05:15 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class MidOrderRatioBuyMoney(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['buy_superorder_money', 'buy_bigorder_money', 'buy_midorder_money', 'buy_smallorder_money']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        sup = data['buy_superorder_money'].iloc[-1]
        big = data['buy_bigorder_money'].iloc[-1]
        mid = data['buy_midorder_money'].iloc[-1]
        small = data['buy_smallorder_money'].iloc[-1]
        
        sup.fillna(0, inplace = True)
        big.fillna(0, inplace = True)
        mid.fillna(0, inplace = True)
        small.fillna(0, inplace = True)
        
        sup = sup.values
        big = big.values
        mid = mid.values
        small = small.values
        
        temp = cross4(sup+big + mid + small)
        
        factor = np.nanmean(mid/temp)
        
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 10:07:47 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class OFIR(FutureFactor):

    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IC':['OrderFlowImbalanceRatioLv1']} 
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    

    def calculate(self, data):
        factor = data['OrderFlowImbalanceRatioLv1_cont_IC'].iloc[-1]


        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 09:28:06 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd



class BASWeighted(FutureFactor):

    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IC':['BASWeighted']} 
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    

    def calculate(self, data):
        factor = data['BASWeighted_cont_IC'].iloc[-1]


        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 16:50:45 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class Futures_Std_30(FutureFactor):

    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IC':['close']} 
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    

    def calculate(self, data):
        cl = data['close_cont_IC'].iloc[-31:].values
        ret = cl[1:]/cl[:-1]
        factor = np.nanstd(ret)


        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 13:42:04 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class Spot_mom_30(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']} 
    normalize_size = 1
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        
        hclose = data['close_000905.SH'].iloc[-31:].values
        
        factor = (hclose[-1] / hclose[1] - 1)

        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 13:17:29 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class SuperOrderRatioSell_5(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['sell_superorder_count', 'sell_bigorder_count', 'sell_midorder_count', 'sell_smallorder_count']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        sup = data['sell_superorder_count'].iloc[-240:]
        big = data['sell_bigorder_count'].iloc[-240:]
        mid = data['sell_midorder_count'].iloc[-240:]
        small = data['sell_smallorder_count'].iloc[-240:]
        
        sup.fillna(0, inplace = True)
        big.fillna(0, inplace = True)
        mid.fillna(0, inplace = True)
        small.fillna(0, inplace = True)
        
        date = str(data['sell_midorder_count'].index.date[-1]) 
        sup = sup.loc[date]
        big = big.loc[date]
        mid = mid.loc[date]
        small = small.loc[date]
        if len(big)<=5:
            if len(big) == 1:
                sup = sup.values
                big = big.values
                mid = mid.values
                small = small.values
            else:
                sup = np.nanmean(sup.values, axis = 0)
                big = np.nanmean(big.values, axis = 0)
                mid = np.nanmean(mid.values, axis = 0)
                small = np.nanmean(small.values, axis = 0)
        else:
            sup = np.nanmean(sup.iloc[-5:].values, axis = 0)
            big = np.nanmean(big.iloc[-5:].values, axis = 0)
            mid = np.nanmean(mid.iloc[-5:].values, axis = 0)
            small = np.nanmean(small.iloc[-5:].values, axis = 0)

        temp = cross4(sup+big+mid+small)
        
        factor = np.nanmean(sup/temp)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 11:04:58 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class SuperOrderRatioSellMoney_Weighted_5(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['sell_superorder_money', 'sell_bigorder_money', 'sell_midorder_money', 'sell_smallorder_money', 'weight']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        sup = data['sell_superorder_money'].iloc[-240:]
        big = data['sell_bigorder_money'].iloc[-240:]
        mid = data['sell_midorder_money'].iloc[-240:]
        small = data['sell_smallorder_money'].iloc[-240:]
        
        sup.fillna(0, inplace = True)
        big.fillna(0, inplace = True)
        mid.fillna(0, inplace = True)
        small.fillna(0, inplace = True)
        
        date = str(data['sell_superorder_money'].index.date[-1]) 
        sup = sup.loc[date]
        big = big.loc[date]
        mid = mid.loc[date]
        small = small.loc[date]
        if len(big)<=5:
            if len(big) == 1:
                sup = sup.values
                big = big.values
                mid = mid.values
                small = small.values
            else:
                sup = np.nanmean(sup.values, axis = 0)
                big = np.nanmean(big.values, axis = 0)
                mid = np.nanmean(mid.values, axis = 0)
                small = np.nanmean(small.values, axis = 0)
        else:
            sup = np.nanmean(sup.iloc[-5:].values, axis = 0)
            big = np.nanmean(big.iloc[-5:].values, axis = 0)
            mid = np.nanmean(mid.iloc[-5:].values, axis = 0)
            small = np.nanmean(small.iloc[-5:].values, axis = 0)

        temp = cross4(sup+big+mid+small)
        
        factor = np.nanmean(data['weight'].iloc[-1].values * sup/temp)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 13:02:55 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class SmallOrderRatioSell_5(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['sell_superorder_count', 'sell_bigorder_count', 'sell_midorder_count', 'sell_smallorder_count']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        sup = data['sell_superorder_count'].iloc[-240:]
        big = data['sell_bigorder_count'].iloc[-240:]
        mid = data['sell_midorder_count'].iloc[-240:]
        small = data['sell_smallorder_count'].iloc[-240:]
        
        sup.fillna(0, inplace = True)
        big.fillna(0, inplace = True)
        mid.fillna(0, inplace = True)
        small.fillna(0, inplace = True)
        
        date = str(data['sell_midorder_count'].index.date[-1]) 
        sup = sup.loc[date]
        big = big.loc[date]
        mid = mid.loc[date]
        small = small.loc[date]
        if len(big)<=5:
            if len(big) == 1:
                sup = sup.values
                big = big.values
                mid = mid.values
                small = small.values
            else:
                sup = np.nanmean(sup.values, axis = 0)
                big = np.nanmean(big.values, axis = 0)
                mid = np.nanmean(mid.values, axis = 0)
                small = np.nanmean(small.values, axis = 0)
        else:
            sup = np.nanmean(sup.iloc[-5:].values, axis = 0)
            big = np.nanmean(big.iloc[-5:].values, axis = 0)
            mid = np.nanmean(mid.iloc[-5:].values, axis = 0)
            small = np.nanmean(small.iloc[-5:].values, axis = 0)

        temp = cross4(sup+big+mid+small)
        
        factor = np.nanmean(small/temp)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 14:19:54 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class ret(FutureFactor):

    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IC':['close']} 
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    

    def calculate(self, data):
        factor1 = data['close_cont_IC'].iloc[-3:].values

        factor = factor1[-1] / factor1[-2] - 1

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 10:40:33 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class SellUnique_Weighted(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['SellUniqueOrderNum', 'SellTradeNum', 'weight']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        a = data['SellUniqueOrderNum'].iloc[-1]
        b = data['SellTradeNum'].iloc[-1]
        w = data['weight'].iloc[-1].values
        #a.fillna(0, inplace = True)
        #b.fillna(0, inplace = True)
        
        a = a.values
        b = b.values
        temp = cross(a/b)
        
        factor = np.nanmean(w*temp)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 16:41:40 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class BigOrderRatioSell_Weighted(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['sell_superorder_count', 'sell_bigorder_count', 'sell_midorder_count', 'sell_smallorder_count', 'weight']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        sup = data['sell_superorder_count'].iloc[-1]
        big = data['sell_bigorder_count'].iloc[-1]
        mid = data['sell_midorder_count'].iloc[-1]
        small = data['sell_smallorder_count'].iloc[-1]
        weight = data['weight'].iloc[-1].values
        
        sup.fillna(0, inplace = True)
        big.fillna(0, inplace = True)
        mid.fillna(0, inplace = True)
        small.fillna(0, inplace = True)
        
        temp = cross4(sup.values+big.values + mid.values + small.values)
        
        factor = np.nanmean(weight * big/temp)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 13:41:17 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class Spot_mom_10(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']} 
    normalize_size = 1
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        
        hclose = data['close_000905.SH'].iloc[-11:].values
        
        factor = (hclose[-1] / hclose[1] - 1)

        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 17:55:55 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class HighVolumeCount(FutureFactor):

    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IC':['HighVolumeCount']} 
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    

    def calculate(self, data):
        factor = data['HighVolumeCount_cont_IC'].iloc[-1]



        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 10:42:15 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class SellUnique_Weighted_5(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['SellUniqueOrderNum', 'SellTradeNum', 'weight']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀

    def calculate(self, data):
            a = data['SellUniqueOrderNum'].iloc[-240:]

            date = str(a.index.date[-1])
            a1 = a.loc[date].values
            a2 = data['SellTradeNum'].loc[date].values
            if len(a1)<=5:
                if len(a1) == 1:
                    pass
                else:
                    a1 = np.nanmean(a1, axis = 0)
                    a2 = np.nanmean(a2, axis = 0)
            else:
                a1 = np.nanmean(a1[-5:], axis = 0)
                a2 = np.nanmean(a2[-5:], axis = 0)

            a2[abs(a2)<1e-8] = np.nan
            a = cross(a1/a2)

            factor = np.nanmean(a*data['weight'].iloc[-1].values)

            return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 14:58:52 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class turnover_mean_30(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['turnover_rate']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        factor = np.nanmean(data['turnover_rate'].iloc[-30:], axis = 0)
        
        return np.nanmean(factor)
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 10:20:48 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class PxVolCorr_Weighted(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['PxVolCorr', 'weight']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        a = data['PxVolCorr'].iloc[-1]
        a = a.fillna(0)
        a = a.values
 
        factor = np.nanmean(data['weight'].iloc[-1].values*a)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 11:07:01 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd



class BigOrderRatioBuy(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['buy_superorder_count', 'buy_bigorder_count', 'buy_midorder_count', 'buy_smallorder_count']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        sup = data['buy_superorder_count'].iloc[-1]
        big = data['buy_bigorder_count'].iloc[-1]
        mid = data['buy_midorder_count'].iloc[-1]
        small = data['buy_smallorder_count'].iloc[-1]
        
        sup.fillna(0, inplace = True)
        big.fillna(0, inplace = True)
        mid.fillna(0, inplace = True)
        small.fillna(0, inplace = True)
        
        temp = cross4(sup.values+big.values + mid.values + small.values)
        
        factor = np.nanmean(big/temp)
        
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 18:14:53 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class MidOrderRatioBuyMoney_5(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['buy_superorder_money', 'buy_bigorder_money', 'buy_midorder_money', 'buy_smallorder_money', 'weight']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        sup = data['buy_superorder_money'].iloc[-240:]
        big = data['buy_bigorder_money'].iloc[-240:]
        mid = data['buy_midorder_money'].iloc[-240:]
        small = data['buy_smallorder_money'].iloc[-240:]
        
        sup.fillna(0, inplace = True)
        big.fillna(0, inplace = True)
        mid.fillna(0, inplace = True)
        small.fillna(0, inplace = True)
        
        date = str(data['buy_superorder_money'].index.date[-1]) 
        sup = sup.loc[date]
        big = big.loc[date]
        mid = mid.loc[date]
        small = small.loc[date]
        if len(big)<=5:
            if len(big) == 1:
                sup = sup.values
                big = big.values
                mid = mid.values
                small = small.values
            else:
                sup = np.nanmean(sup.values, axis = 0)
                big = np.nanmean(big.values, axis = 0)
                mid = np.nanmean(mid.values, axis = 0)
                small = np.nanmean(small.values, axis = 0)
        else:
            sup = np.nanmean(sup.iloc[-5:].values, axis = 0)
            big = np.nanmean(big.iloc[-5:].values, axis = 0)
            mid = np.nanmean(mid.iloc[-5:].values, axis = 0)
            small = np.nanmean(small.iloc[-5:].values, axis = 0)

        temp = cross4(sup+big+mid+small)
        
        factor = np.nanmean(mid/temp)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 16:23:46 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class BuyUnique_Weighted(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'BuyTradeNum', 'weight']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        a = data['BuyUniqueOrderNum'].iloc[-1]
        b = data['BuyTradeNum'].iloc[-1]
        w = data['weight'].iloc[-1].values
        #a.fillna(0, inplace = True)
        #b.fillna(0, inplace = True)
        
        a = a.values
        b = b.values
        temp = cross(a/b)
        
        factor = np.nanmean(w*temp)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 10:54:25 2021

@author: appadmin
"""


import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class BidAskAmtRatio_5(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['Bid1AmtMean', 'Ask1AmtMean']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        date = str(data['Bid1AmtMean'].index.date[-1]) 
        a1 = data['Bid1AmtMean'].loc[date] 
        a2 = data['Ask1AmtMean'].loc[date] 
        if len(a1)<=5:
            if len(a1) == 1:
                pass
            else:
                a1 = np.nanmean(a1, axis = 0)
                a2 = np.nanmean(a2, axis = 0)
        else:
            a1 = np.nanmean(a1.iloc[-5:], axis = 0)
            a2 = np.nanmean(a2.iloc[-5:], axis = 0)
            
        a2[abs(a2)<1e-8] = np.nan
        a = cross(a1/a2)
        #factor = a.mean(axis = 1)
        factor = np.nanmean(a)       
        
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 13:52:32 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class StkVol(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['stk_volatility']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        factor = np.nanmean(data['stk_volatility'].iloc[-1])
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 14:30:11 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class rsi(FutureFactor):

    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IC':['close']} 
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    

    def calculate(self, data):
        hclose = data['close_cont_IC'].iloc[-31:].values
        ret = hclose[1:]/hclose[:-1] - 1
        temp_rsi = (ret>0)
        temp_rsi2 = (ret<=0)
        
        a = np.nanmean(temp_rsi*ret, axis = 0)
        b = np.nanmean(temp_rsi2*ret, axis = 0)*(-1)
        factor = (a/(a+b))

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 09:36:57 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class MidOrderRatioSellMoney_Weighted(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['sell_superorder_money', 'sell_bigorder_money', 'sell_midorder_money', 'sell_smallorder_money', 'weight']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        sup = data['sell_superorder_money'].iloc[-1]
        big = data['sell_bigorder_money'].iloc[-1]
        mid = data['sell_midorder_money'].iloc[-1]
        small = data['sell_smallorder_money'].iloc[-1]
        
        sup.fillna(0, inplace = True)
        big.fillna(0, inplace = True)
        mid.fillna(0, inplace = True)
        small.fillna(0, inplace = True)
        
        sup = sup.values
        big = big.values
        mid = mid.values
        small = small.values
        
        temp = cross4(sup+big + mid + small)
        
        factor = np.nanmean(data['weight'].iloc[-1]*mid/temp)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 10:35:26 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd



class PxVolCorr_Weighted_5(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['PxVolCorr', 'weight']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        date = str(data['PxVolCorr'].index.date[-1]) 
        a1 = data['PxVolCorr'].loc[date] 
        a1.fillna(0, inplace = True)
        a1 = a1.values
        a1 = cross(a1)
        if len(a1)<=5:
            if len(a1) == 1:
                pass
            else:
                a1 = np.nanmean(a1, axis = 0)

        else:
            a1 = np.nanmean(a1[-5:], axis = 0)


        
        #factor = a.mean(axis = 1)
        factor = np.nanmean(a1*data['weight'].iloc[-1].values)       
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 11:20:34 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class SmallOrderRatioSell(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['sell_superorder_count', 'sell_bigorder_count', 'sell_midorder_count', 'sell_smallorder_count']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        sup = data['sell_superorder_count'].iloc[-1]
        big = data['sell_bigorder_count'].iloc[-1]
        mid = data['sell_midorder_count'].iloc[-1]
        small = data['sell_smallorder_count'].iloc[-1]
        
        sup.fillna(0, inplace = True)
        big.fillna(0, inplace = True)
        mid.fillna(0, inplace = True)
        small.fillna(0, inplace = True)
        
        temp = cross4(sup.values+big.values + mid.values + small.values)
        
        factor = np.nanmean(small/temp)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 14:03:16 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd



class WeightedBuySell_Weighted(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['WeightBuyOrderQtySumMean', 'WeightSellOrderQtySumMean', 'weight']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        a = data['WeightBuyOrderQtySumMean'].iloc[-1] 
        b = data['WeightSellOrderQtySumMean'].iloc[-1]
        w = data['weight'].iloc[-1].values
        a.fillna(0, inplace = True)
        b.fillna(0, inplace = True)
        a = a.values
        b = b.values
        factor = cross(w*a/b)       
        
        return np.nanmean(factor)
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 10:51:00 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd



class SmallOrderRatioBuyMoney_5(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['buy_superorder_money', 'buy_bigorder_money', 'buy_midorder_money', 'buy_smallorder_money', 'weight']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        sup = data['buy_superorder_money'].iloc[-240:]
        big = data['buy_bigorder_money'].iloc[-240:]
        mid = data['buy_midorder_money'].iloc[-240:]
        small = data['buy_smallorder_money'].iloc[-240:]
        
        sup.fillna(0, inplace = True)
        big.fillna(0, inplace = True)
        mid.fillna(0, inplace = True)
        small.fillna(0, inplace = True)
        
        date = str(data['buy_superorder_money'].index.date[-1]) 
        sup = sup.loc[date]
        big = big.loc[date]
        mid = mid.loc[date]
        small = small.loc[date]
        if len(big)<=5:
            if len(big) == 1:
                sup = sup.values
                big = big.values
                mid = mid.values
                small = small.values
            else:
                sup = np.nanmean(sup.values, axis = 0)
                big = np.nanmean(big.values, axis = 0)
                mid = np.nanmean(mid.values, axis = 0)
                small = np.nanmean(small.values, axis = 0)
        else:
            sup = np.nanmean(sup.iloc[-5:].values, axis = 0)
            big = np.nanmean(big.iloc[-5:].values, axis = 0)
            mid = np.nanmean(mid.iloc[-5:].values, axis = 0)
            small = np.nanmean(small.iloc[-5:].values, axis = 0)

        temp = cross4(sup+big+mid+small)
        
        factor = np.nanmean(small/temp)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 17:32:38 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class Futures_Std_5(FutureFactor):

    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IC':['close']} 
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    

    def calculate(self, data):
        cl = data['close_cont_IC'].iloc[-6:].values
        ret = cl[1:]/cl[:-1]
        factor = np.nanstd(ret)


        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 14:20:11 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class ret_to_amount(FutureFactor):

    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IC':['close', 'amount']} 
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    

    def calculate(self, data):
        factor1 = data['close_cont_IC'].iloc[-3:].values

        factor = (factor1[-1] / factor1[-2] - 1)/data['amount_cont_IC'].iloc[-1]
        if ~np.isfinite(factor):
            factor = np.nan

        return np.abs(factor)

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 11:24:18 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class SuperOrderRatioSell(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['sell_superorder_count', 'sell_bigorder_count', 'sell_midorder_count', 'sell_smallorder_count']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        sup = data['sell_superorder_count'].iloc[-1]
        big = data['sell_bigorder_count'].iloc[-1]
        mid = data['sell_midorder_count'].iloc[-1]
        small = data['sell_smallorder_count'].iloc[-1]
        
        sup.fillna(0, inplace = True)
        big.fillna(0, inplace = True)
        mid.fillna(0, inplace = True)
        small.fillna(0, inplace = True)
        
        temp = cross4(sup.values+big.values + mid.values + small.values)
        
        factor = np.nanmean(sup/temp)
        
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 11:06:40 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd



class BidAskMean(FutureFactor):

    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IC':['BidAskMean']} 
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    

    def calculate(self, data):
        
        factor = np.nanmean(data['BidAskMean_cont_IC'].iloc[-1])
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 14:41:54 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd




class BigOrderRatioBuyMoney_5(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['buy_superorder_money', 'buy_bigorder_money', 'buy_midorder_money', 'buy_smallorder_money', 'weight']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        sup = data['buy_superorder_money'].iloc[-240:]
        big = data['buy_bigorder_money'].iloc[-240:]
        mid = data['buy_midorder_money'].iloc[-240:]
        small = data['buy_smallorder_money'].iloc[-240:]
        
        sup.fillna(0, inplace = True)
        big.fillna(0, inplace = True)
        mid.fillna(0, inplace = True)
        small.fillna(0, inplace = True)
        
        date = str(data['buy_superorder_money'].index.date[-1]) 
        sup = sup.loc[date]
        big = big.loc[date]
        mid = mid.loc[date]
        small = small.loc[date]
        if len(big)<=5:
            if len(big) == 1:
                sup = sup.values
                big = big.values
                mid = mid.values
                small = small.values
            else:
                sup = np.nanmean(sup.values, axis = 0)
                big = np.nanmean(big.values, axis = 0)
                mid = np.nanmean(mid.values, axis = 0)
                small = np.nanmean(small.values, axis = 0)
        else:
            sup = np.nanmean(sup.iloc[-5:].values, axis = 0)
            big = np.nanmean(big.iloc[-5:].values, axis = 0)
            mid = np.nanmean(mid.iloc[-5:].values, axis = 0)
            small = np.nanmean(small.iloc[-5:].values, axis = 0)

        temp = cross4(sup+big+mid+small)
        
        factor = np.nanmean(big/temp)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 16:16:50 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class BigOrderRatioSellMoney_Weighted(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['sell_superorder_money', 'sell_bigorder_money', 'sell_midorder_money', 'sell_smallorder_money', 'weight']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        sup = data['sell_superorder_money'].iloc[-1]
        big = data['sell_bigorder_money'].iloc[-1]
        mid = data['sell_midorder_money'].iloc[-1]
        small = data['sell_smallorder_money'].iloc[-1]
        weight = data['weight'].iloc[-1].values
        
        sup.fillna(0, inplace = True)
        big.fillna(0, inplace = True)
        mid.fillna(0, inplace = True)
        small.fillna(0, inplace = True)
        
        temp = cross4(sup.values+big.values + mid.values + small.values)
        
        factor = np.nanmean(weight * big/temp)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 10:37:55 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class RetSkew(FutureFactor):

    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IC':['RetSkew']} 
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    

    def calculate(self, data):
        factor = data['RetSkew_cont_IC'].iloc[-1]

        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 09:09:08 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class AbsPx1Min_Weighted_5(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['AbsPxPath', 'weight', 'close']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    

    def calculate(self, data):
        weight = data['weight'].iloc[-1].values
        date = str(data['AbsPxPath'].index.date[-1]) 
        a1 = data['AbsPxPath'].loc[date].values
        a2 = data['close'].loc[date].values
        if len(a1)<=5:
            if len(a1) == 1:
                pass
            else:
                a1 = np.nanmean(a1, axis = 0)
                a2 = np.nanmean(a2, axis = 0)
        else:
            a1 = np.nanmean(a1[-5:], axis = 0)
            a2 = np.nanmean(a2[-5:], axis = 0)
            
        a2[abs(a2)<1e-8] = np.nan
        a = cross(a1/a2)
        #factor = a.mean(axis = 1)
        factor = np.nanmean(weight*a)

        return factor
    
##########
