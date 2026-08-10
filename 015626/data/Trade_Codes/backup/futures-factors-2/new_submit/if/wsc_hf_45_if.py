import numpy as np
import numpy.ma as ma
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_45_if(FutureFactor):
    # 盘口卖单的vwap与盘口买单的vwap之比

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['WeightBuyMoneySumMean', 'WeightBuyOrderQtySumMean', 'WeightSellMoneySumMean', 'WeightSellOrderQtySumMean', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        WeightBuyMoneySumMean = data['WeightBuyMoneySumMean'].values[-1]
        WeightBuyOrderQtySumMean = data['WeightBuyOrderQtySumMean'].values[-1]
        WeightSellMoneySumMean = data['WeightSellMoneySumMean'].values[-1]
        WeightSellOrderQtySumMean = data['WeightSellOrderQtySumMean'].values[-1]
        weight = data['weight'].values[-1]
        
        temp_bid_price = WeightBuyMoneySumMean / replace_zero(WeightBuyOrderQtySumMean)
        temp_ask_price = WeightSellMoneySumMean / replace_zero(WeightSellOrderQtySumMean)
        temp_vwap_ratio = temp_bid_price / replace_zero(temp_ask_price) - 1
        factor = np.nansum(temp_vwap_ratio * weight)
        return factor