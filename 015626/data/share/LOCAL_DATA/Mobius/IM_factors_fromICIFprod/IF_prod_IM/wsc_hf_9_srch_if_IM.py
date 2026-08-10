import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero


class wsc_hf_9_srch_if_IM(FutureFactor):

    """
    ts_mean(-ts_skew(bn_r, 20), 5)
    """
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeNum', 'SellTradeNum']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False

    def calculate(self, data):
        buy_trade_num = data['BuyTradeNum'].values[-25:]
        sell_trade_num = data['SellTradeNum'].values[-25:]

        bn = np.nansum(buy_trade_num, axis=1)
        sn = np.nansum(sell_trade_num, axis=1)
        bn_r = bn / (bn + sn)
        
        factor_raw = -ts_skew(bn_r, 20)
        factor = np.nanmean(factor_raw[-5:])
        return factor