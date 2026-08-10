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


class position_if(FutureFactor):

    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IF':['OpenInterest']} 
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    

    def calculate(self, data):
        factor = data['OpenInterest_cont_IF'].iloc[-1]

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

class SmallOrderRatioSell_if(FutureFactor):

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
        
        temp = cross4_if(sup.values+big.values + mid.values + small.values)
        
        factor = np.nanmean(small/temp)
        
        return factor
##########
import numpy as np
from operators_cc import *
from future_factor import FutureFactor


class SmallOrderRatioBuy_if(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_superorder_count', 'buy_bigorder_count', 'buy_midorder_count', 'buy_smallorder_count']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        sup = data['buy_superorder_count'].fillna(0).values[-1]
        big = data['buy_bigorder_count'].fillna(0).values[-1]
        mid = data['buy_midorder_count'].fillna(0).values[-1]
        small = data['buy_smallorder_count'].fillna(0).values[-1]
        
        temp = cross4_if(sup + big + mid + small)
        factor = np.nanmean(small / temp)
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 11:26:31 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class Futures_Std_5_if(FutureFactor):

    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IF':['close']} 
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    

    def calculate(self, data):
        cl = data['close_cont_IF'].iloc[-6:].values
        ret = cl[1:]/cl[:-1]
        factor = np.nanstd(ret)


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



class WeightedBuySell_Weighted_if(FutureFactor):

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
        factor = cross_if(w*a/b)       
        
        return np.nanmean(factor)
##########
import numpy as np
from operators_cc import *
from future_factor import FutureFactor


class PxVolCorr_Weighted_5_if(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight', 'PxVolCorr']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        PxVolCorr = data['PxVolCorr'].iloc[-5:]
        weight = data['weight'].values[-1]
        
        date = str(PxVolCorr.index[-1].date())
        PxVolCorr = PxVolCorr.loc[date].values
        a = cross_if(PxVolCorr)
        if a.shape[0] > 1:
            a = np.nanmean(a, axis=0)
        factor = np.nanmean(a * weight)
        
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


class ret_to_amount_if(FutureFactor):

    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IF':['close', 'amount']} 
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    

    def calculate(self, data):
        factor1 = data['close_cont_IF'].iloc[-3:].values

        factor = (factor1[-1] / factor1[-2] - 1)/data['amount_cont_IF'].iloc[-1]
        if ~np.isfinite(factor):
            factor = np.nan

        return np.abs(factor)

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 11:32:10 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class HighVolumeCount_if(FutureFactor):

    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IF':['HighVolumeCount']} 
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    

    def calculate(self, data):
        factor = data['HighVolumeCount_cont_IF'].iloc[-1]



        return factor
##########
import numpy as np
from operators_cc import *
from future_factor import FutureFactor


class SellUnique_Weighted_if(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight', 'SellUniqueOrderNum', 'SellTradeNum']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-1]
        SellTradeNum = data['SellTradeNum'].values[-1]
        weight = data['SellTradeNum'].values[-1]

        a = cross_if(weight * SellUniqueOrderNum / SellTradeNum)
        factor = np.nanmean(a)
        
        return factor

##########
from future_factor import FutureFactor


class RetSkew_if(FutureFactor):

    data_type = 'Future'  # 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IF':['RetSkew']} 
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None    

    def calculate(self, data):
        factor = data['RetSkew_cont_IF'].values[-1]

        return factor

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

class SuperOrderRatioSell_Weighted_if(FutureFactor):

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
        
        temp = cross4_if(sup.values+big.values + mid.values + small.values)
        
        factor = np.nanmean(weight * sup/temp)
        
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 10:12:39 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class BidAskMean_if(FutureFactor):

    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IF':['BidAskMean']} 
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    

    def calculate(self, data):
        
        factor = np.nanmean(data['BidAskMean_cont_IF'].iloc[-1])
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 11:29:16 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class Futures_mom_10_if(FutureFactor):

    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IF':['close']} 
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    

    def calculate(self, data):
        cl = data['close_cont_IF'].iloc[-11:].values
        ret = cl[-1]/cl[0]-1


        return ret
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


class SuperOrderRatioBuy_5_if(FutureFactor):

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

        temp = cross4_if(sup+big+mid+small)
        
        factor = np.nanmean(sup/temp)
        
        return factor
##########
import numpy as np
from operators_cc import *
from future_factor import FutureFactor


class MidOrderRatioBuyMoney_if(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_superorder_money', 'buy_bigorder_money', 'buy_midorder_money', 'buy_smallorder_money']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        sup = data['buy_superorder_money'].fillna(0).values[-1]
        big = data['buy_bigorder_money'].fillna(0).values[-1]
        mid = data['buy_midorder_money'].fillna(0).values[-1]
        small = data['buy_smallorder_money'].fillna(0).values[-1]
        
        temp = cross4_if(sup + big + mid + small)
        factor = np.nanmean(mid / temp)
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

class position_diff_if(FutureFactor):

    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IF':['OpenInterest']} 
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    

    def calculate(self, data):
        factor1 = data['OpenInterest_cont_IF'].iloc[-3:].values

        factor = factor1[-1] - factor1[-2]

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

class SuperOrderRatioSellMoney_Weighted_if(FutureFactor):

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
        
        temp = cross4_if(sup.values+big.values + mid.values + small.values)
        
        factor = np.nanmean(weight * sup/temp)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 11:24:01 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class Futures_Std_30_if(FutureFactor):

    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IF':['close']} 
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    

    def calculate(self, data):
        cl = data['close_cont_IF'].iloc[-31:].values
        ret = cl[1:]/cl[:-1]
        factor = np.nanstd(ret)


        return factor
##########
import numpy as np
from operators_cc import *
from future_factor import FutureFactor


class MidOrderRatioSellMoney_Weighted_if(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight', 'sell_superorder_money', 'sell_bigorder_money', 'sell_midorder_money', 'sell_smallorder_money']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        sup = data['sell_superorder_money'].fillna(0).values[-1]
        big = data['sell_bigorder_money'].fillna(0).values[-1]
        mid = data['sell_midorder_money'].fillna(0).values[-1]
        small = data['sell_smallorder_money'].fillna(0).values[-1]
        weight = data['weight'].values[-1]

        temp = cross4_if(sup + big + mid + small)
        factor = np.nanmean(weight * mid / temp)
        
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 11:15:04 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class BuyUnique_Weighted_if(FutureFactor):

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
        temp = cross_if(w*a/b)
        
        factor = np.nanmean(temp)
        
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

class SuperOrderRatioBuyMoney_Weighted_if(FutureFactor):

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
        
        temp = cross4_if(sup.values+big.values + mid.values + small.values)
        
        factor = np.nanmean(weight * sup/temp)
        
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


class ret_if(FutureFactor):

    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IF':['close']} 
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    

    def calculate(self, data):
        factor1 = data['close_cont_IF'].iloc[-3:].values

        factor = factor1[-1] / factor1[-2] - 1

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 11:14:44 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd



class BuyUnique_Weighted_5_if(FutureFactor):

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
        a = cross_if(a1/a2)

        factor = np.nanmean(a * data['weight'].iloc[-1].values)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 10:24:30 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class BidAskAmtRatio_if(FutureFactor):

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
        a = data['Bid1AmtMean'].iloc[-1] 
        b = data['Ask1AmtMean'].iloc[-1]
        #w = data['weight'].iloc[-1].values
        a.fillna(0, inplace = True)
        b.fillna(0, inplace = True)
        a = a.values
        b = b.values
        factor = cross_if(a/b)       
        
        return np.nanmean(factor)
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 10:54:05 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class BigOrderRatioBuy_Weighted_5_if(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['buy_superorder_count', 'buy_bigorder_count', 'buy_midorder_count', 'buy_smallorder_count', 'weight']
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
        
        date = str(data['buy_bigorder_count'].index.date[-1]) 
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

        temp = cross4_if(sup+big+mid+small)
        
        factor = np.nanmean(data['weight'].iloc[-1].values * big/temp)
        
        return factor
##########
import numpy as np
from operators_cc import *
from future_factor import FutureFactor


class MidOrderRatioBuy_Weighted_if(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight', 'buy_superorder_count', 'buy_bigorder_count', 'buy_midorder_count', 'buy_smallorder_count']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        sup = data['buy_superorder_count'].fillna(0).values[-1]
        big = data['buy_bigorder_count'].fillna(0).values[-1]
        mid = data['buy_midorder_count'].fillna(0).values[-1]
        small = data['buy_smallorder_count'].fillna(0).values[-1]
        weight = data['weight'].values[-1]
        
        temp = cross4_if(sup + big + mid + small)
        factor = np.nanmean(weight * mid / temp)
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


class sjx_if(FutureFactor):

    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IF':['close']} 
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    

    def calculate(self, data):
        hclose = data['close_cont_IF'].iloc[-121:].values
        factor = np.nanmean(hclose[-5:]) - np.nanmean(hclose[-120:])

        return factor

##########
from future_factor import FutureFactor


class OFIR_if(FutureFactor):

    data_type = 'Future'  # 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IF':['OrderFlowImbalanceRatioLv1']} 
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None    

    def calculate(self, data):
        factor = data['OrderFlowImbalanceRatioLv1_cont_IF'].values[-1]

        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 10:29:50 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class BigOrderRatioBuyMoney_Weighted_if(FutureFactor):

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
        weight = data['weight'].iloc[-1]
        
        sup.fillna(0, inplace = True)
        big.fillna(0, inplace = True)
        mid.fillna(0, inplace = True)
        small.fillna(0, inplace = True)
        
        temp = cross4_if(sup.values+big.values + mid.values + small.values)
        
        factor = np.nanmean(weight*big/temp)
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 11:32:28 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class IndexCorr_if(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['stk_index_corr_hs300']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        
        factor = np.nanmean(data['stk_index_corr_hs300'].iloc[-1])
        
        return factor
##########
import numpy as np
from operators_cc import *
from future_factor import FutureFactor
from help_functions_wsc import replace_zero


class MidOrderRatioSellMoney_5_if(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['sell_superorder_money', 'sell_bigorder_money', 'sell_midorder_money', 'sell_smallorder_money']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        sup = data['sell_superorder_money'].fillna(0).iloc[-5:]
        big = data['sell_bigorder_money'].fillna(0).iloc[-5:]
        mid = data['sell_midorder_money'].fillna(0).iloc[-5:]
        small = data['sell_smallorder_money'].fillna(0).iloc[-5:]
        
        date = str(sup.index[-1].date())
        sup = sup.loc[date].values
        big = big.loc[date].values
        mid = mid.loc[date].values
        small = small.loc[date].values
        
        if sup.shape[0] > 1:
            sup = np.nanmean(sup, axis = 0)
            big = np.nanmean(big, axis = 0)
            mid = np.nanmean(mid, axis = 0)
            small = np.nanmean(small, axis = 0)
        temp = cross4_if(replace_zero(sup + big + mid + small))
        factor = np.nanmean(mid / temp)
        
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


class SuperOrderRatioSellMoney_5_if(FutureFactor):

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

        temp = cross4_if(sup+big+mid+small)
        
        factor = np.nanmean(sup/temp)
        
        return factor
##########
import numpy as np
from operators_cc import *
from future_factor import FutureFactor


class MidOrderRatioSell_if(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['sell_superorder_count', 'sell_bigorder_count', 'sell_midorder_count', 'sell_smallorder_count']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        sup = data['sell_superorder_count'].fillna(0).values[-1]
        big = data['sell_bigorder_count'].fillna(0).values[-1]
        mid = data['sell_midorder_count'].fillna(0).values[-1]
        small = data['sell_smallorder_count'].fillna(0).values[-1]

        temp = cross4_if(sup + big + mid + small)
        factor = np.nanmean(mid / temp)
        
        return factor

##########
import numpy as np
from operators_cc import *
from future_factor import FutureFactor


class PxVolCorr_if(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['PxVolCorr']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        PxVolCorr = data['PxVolCorr'].values[-1]

        a = cross_if(PxVolCorr)
        factor = np.nanmean(a)
        
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 11:09:24 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class BigOrderRatioSell_Weighted_if(FutureFactor):

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
        
        temp = cross4_if(sup.values+big.values + mid.values + small.values)
        
        factor = np.nanmean(weight * big/temp)
        
        return factor
##########
import numpy as np
from operators_cc import *
from future_factor import FutureFactor
from help_functions_wsc import replace_zero


class SmallOrderRatioSell_5_if(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['sell_superorder_count', 'sell_bigorder_count', 'sell_midorder_count', 'sell_smallorder_count']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        sup = data['sell_superorder_count'].fillna(0).iloc[-5:]
        big = data['sell_bigorder_count'].fillna(0).iloc[-5:]
        mid = data['sell_midorder_count'].fillna(0).iloc[-5:]
        small = data['sell_smallorder_count'].fillna(0).iloc[-5:]
        
        date = str(sup.index[-1].date())
        sup = sup.loc[date].values
        big = big.loc[date].values
        mid = mid.loc[date].values
        small = small.loc[date].values
        
        if sup.shape[0] > 1:
            sup = np.nanmean(sup, axis = 0)
            big = np.nanmean(big, axis = 0)
            mid = np.nanmean(mid, axis = 0)
            small = np.nanmean(small, axis = 0)
        temp = cross4_if(replace_zero(sup + big + mid + small))
        factor = np.nanmean(small / temp)
        
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

class amount_sum_if(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['amount']
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        a = data['amount'].iloc[-1].values 
        factor = np.nansum(a)
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 10:14:16 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class BASWeighted_if(FutureFactor):

    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IF':['BASWeighted']} 
    normalize_size = 1 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None# normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = False # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    

    def calculate(self, data):
        factor = data['BASWeighted_cont_IF'].iloc[-1]


        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 11:01:13 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class BigOrderRatioSellMoney_Weighted_5(FutureFactor):

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

        temp = cross4_if(sup+big+mid+small)
        
        factor = np.nanmean(data['weight'].iloc[-1].values * big/temp)
        
        return factor
##########
import numpy as np
from operators_cc import *
from future_factor import FutureFactor


class MidOrderRatioBuyMoney_Weighted_if(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight', 'buy_superorder_money', 'buy_bigorder_money', 'buy_midorder_money', 'buy_smallorder_money']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        sup = data['buy_superorder_money'].fillna(0).values[-1]
        big = data['buy_bigorder_money'].fillna(0).values[-1]
        mid = data['buy_midorder_money'].fillna(0).values[-1]
        small = data['buy_smallorder_money'].fillna(0).values[-1]
        weight = data['weight'].values[-1]
        
        temp = cross4_if(sup + big + mid + small)
        factor = np.nanmean(weight * mid / temp)
        return factor

##########
