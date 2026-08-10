from future_factor import FutureFactor
import numpy as np
import pandas as pd
from operators_wsc_for_srch import *
from operators_cc import *
from scipy.stats import skew



class cf_search18_ih(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [ 'buy_smallorder_money', 'SellTradeMoney', 'sell_smallorder_money_v2', 'weight', 'SellTradeNum', 'SellUniqueOrderNum', 'buy_midorder_money', 'BuyTradeMoney']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        
        sa_to_sun_w = np.nansum(data['SellTradeMoney'].values[-150:] * data['weight'].values[-150:] / r(data['SellUniqueOrderNum'].values[-150:]), axis = 1)
        
        sa_to_sn_w = np.nansum(data['SellTradeMoney'].values[-150:] * data['weight'].values[-150:] / r(data['SellTradeNum'].values[-150:]), axis = 1)
        
        temp1 = ts_corr(sa_to_sun_w, sa_to_sn_w, 65)
        
        temp2 = dema(temp1, 5)[-1]
        
        
        
        bba_3_to_ba_w = np.nansum(data['buy_midorder_money'].values[-1] * data['weight'].values[-1] / r(data['BuyTradeMoney'].values[-1]))
        
        d2 = (np.nansum(data['buy_smallorder_money'].values[-1] + data['sell_smallorder_money_v2'].values[-1]))
        if abs(d2)<1e-9:
            d2 = np.nan
        
        
        bba_4_r = np.nansum(data['buy_smallorder_money'].values[-1]) / d2
        
        factor_raw = (temp2 - bba_3_to_ba_w) -  bba_4_r
        
        return factor_raw
