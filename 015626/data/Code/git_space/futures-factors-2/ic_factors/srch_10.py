from operators_wsc_1_0 import *
import numpy.ma as ma
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *

class srch_10(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeMoney', 'BuyUniqueOrderNum', 'BuyTradeNum', 'buy_smallorder_money', 'buy_bigorder_money', 'sell_bigorder_money_v2','SellUniqueOrderNum','weight']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-81:]
        BuyTradeNum = data['BuyTradeNum'].values[-81:]
        weight = data['weight'].values[-81:]
        bun_to_bn_w = np.nansum(BuyUniqueOrderNum / replace_zero(BuyTradeNum) * weight, axis = 1) 

        buy_smallorder_money = data['buy_smallorder_money'].values[-81:]
        BuyTradeMoney = data['BuyTradeMoney'].values[-81:]
        weight = data['weight'].values[-81:]
        bba_4_to_ba_w = np.nansum(buy_smallorder_money / replace_zero(BuyTradeMoney) * weight, axis = 1)        
        
        buy_bigorder_money = data['buy_bigorder_money'].values[-1]
        sell_bigorder_money_v2 = data['sell_bigorder_money_v2'].values[-1]
        weight = data['weight'].values[-1]
        bba_2_r_w = np.nansum(buy_bigorder_money / replace_zero(buy_bigorder_money + sell_bigorder_money_v2) * weight)
        
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-41:]
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-41:]
        bun_r = np.nansum(BuyUniqueOrderNum, axis = 1) / np.nansum(BuyUniqueOrderNum + SellUniqueOrderNum, axis = 1)
        
        factor =  -min2(sub2(aroon(bun_to_bn_w, bba_4_to_ba_w, 80)[-1], bba_2_r_w), ts_maxmin_distance(bun_r, 40)[-1])
        
        return factor

