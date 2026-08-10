import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_12_srch(FutureFactor):
    # -bba_4_to_ba_w * midpoint(bun_r, 10) / sun_to_sn_w
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeMoney', 'SellTradeNum', 'BuyUniqueOrderNum', 'SellUniqueOrderNum',
                          'buy_smallorder_money', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        BuyTradeMoney = data['BuyTradeMoney'].values[-10:]
        SellTradeNum = data['SellTradeNum'].values[-10:]
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-10:]
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-10:]
        buy_smallorder_money = data['buy_smallorder_money'].values[-10:]
        weight = data['weight'].values[-10:]
        
        bba_4_to_ba_w = np.nansum(buy_smallorder_money / replace_zero(BuyTradeMoney) * weight, axis=1)
        bun_r = np.nansum(BuyUniqueOrderNum, axis=1) / (np.nansum(BuyUniqueOrderNum, axis=1) + np.nansum(SellUniqueOrderNum, axis=1))
        sun_to_sn_w = np.nansum(SellUniqueOrderNum / replace_zero(SellTradeNum) * weight, axis=1)
        
        factor = -bba_4_to_ba_w * midpoint(bun_r, 10) / sun_to_sn_w
        return factor[-1]