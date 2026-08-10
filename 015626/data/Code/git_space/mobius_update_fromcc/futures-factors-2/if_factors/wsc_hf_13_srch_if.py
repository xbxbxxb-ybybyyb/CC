import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero


    
class wsc_hf_13_srch_if(FutureFactor):

    """
    -mul2(sub2(ts_max(bun_r, 5), sun_to_sn), ts_skew(sn, 60))
    """
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'SellUniqueOrderNum', 'weight', 'SellTradeNum']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy_unique_num = data['BuyUniqueOrderNum'].values[-62:]
        sell_unique_num = data['SellUniqueOrderNum'].values[-62:]
        sell_trade_num = data['SellTradeNum'].values[-62:]
        
        bun = np.nansum(buy_unique_num, axis=1)
        sun = np.nansum(sell_unique_num, axis=1)
        sn = np.nansum(sell_trade_num, axis=1)
        bun_r = bun / (bun + sun)
        sun_to_sn = sun / sn

        factor_raw = -(ts_max(bun_r, 5) - sun_to_sn) * ts_skew(sn, 60)
        factor = np.nanmean(factor_raw[-2:])
        return factor