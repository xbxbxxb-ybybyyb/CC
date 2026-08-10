from future_factor import FutureFactor
import pandas as pd
import numpy as np
import numpy.ma as ma

class wyc_ts102_BSMUDMask_hf_IF(FutureFactor):
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close','amount','BuyTradeMoney','SellTradeMoney']
    normalize_size = 800
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy = data['BuyTradeMoney'][-50:].rolling(30,min_periods = 15).sum().values[-20:]
        sell = data['SellTradeMoney'][-50:].rolling(30,min_periods = 15).sum().values[-20:]
        amount = data['amount'][-50:].rolling(30,min_periods = 15).sum().values[-20:]
        bs = buy-sell
        
        ret = data['close'][-26:].pct_change(5).replace([np.inf, -np.inf, 0], np.nan)[-20:].values
        ret_mask = np.nanquantile(ret,0.8,axis = 1)
        ret_mask = np.expand_dims(ret_mask, axis = -1)
        ret_mask = ret <= ret_mask
        down_ret_mask = np.nanquantile(ret,0.2,axis = 1)
        down_ret_mask = np.expand_dims(down_ret_mask, axis = -1)
        down_ret_mask = ret >= down_ret_mask
        
        bs_ret_mask = ma.array(bs, mask = ret_mask)
        amt_ret_mask = ma.array(amount, mask= ret_mask)
        bs_down_ret_mask = ma.array(bs, mask = down_ret_mask)
        amt_down_ret_mask = ma.array(amount, mask= down_ret_mask)
        
        factor = np.nansum(bs_ret_mask, axis = 1) / np.nansum(amt_ret_mask, axis = 1) - np.nansum(bs_down_ret_mask, axis = 1) / np.nansum(amt_down_ret_mask, axis = 1)
        factor[np.isinf(factor)] = np.nan
        factor = -1 * np.nanmean(factor)
        
        return factor 