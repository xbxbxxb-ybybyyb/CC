from future_factor import FutureFactor
import numpy as np
import numpy.ma as ma

class wyc_ts101_BuySMRet_hf_IF_IM(FutureFactor):
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'buy_midorder_money', 'buy_smallorder_money']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy_midorder_money = data['buy_midorder_money'][-60:].values.sum(axis = 0)
        buy_smallorder_money = data['buy_smallorder_money'][-60:].values.sum(axis = 0)
        buy = buy_midorder_money + buy_smallorder_money
        
        close = data['close'].values
        ret = close[-1] / close[-6] - 1
        
        factor_raw_after_mask = ma.array(buy, mask=(ret<=np.nanquantile(ret, 0.8)))
        factor_raw_after_mask = np.nanmean(factor_raw_after_mask)
        
        return factor_raw_after_mask 