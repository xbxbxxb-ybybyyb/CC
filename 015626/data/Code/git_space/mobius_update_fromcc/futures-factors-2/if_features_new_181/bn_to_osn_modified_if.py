
from future_factor import FutureFactor
import numpy as np
import numpy.ma as ma
import pandas as pd
from operators_wsc_1_0 import *
from operators_cc import *
from scipy.stats import skew




class bn_to_osn_modified_if(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [ 'BuyTradeNum', 'SellTradeNum', 'sell_lo_counts']
    normalize_size = 1
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        
        d1 = (np.nansum(data['sell_lo_counts'].values[-1])) 
        
        if abs(d1) <= 1e-9:
            d1 = np.nan
        
        temp = np.nansum((data['BuyTradeNum'].values[-1])) / d1
        
        
        return np.log(temp) if temp > 0 else np.nan

