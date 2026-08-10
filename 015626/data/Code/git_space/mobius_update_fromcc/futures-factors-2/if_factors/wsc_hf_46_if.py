import numpy as np
import numpy.ma as ma
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_46_if(FutureFactor):
    # 盘口卖单的vwap与盘口买单的vwap之比作为mask，之比越小（即买盘挂单均价越接近卖盘）的股票的平均收益率越高越好

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['WeightBuyMoneySumMean', 'WeightBuyOrderQtySumMean', 'WeightSellMoneySumMean', 'WeightSellOrderQtySumMean', 'close']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        WeightBuyMoneySumMean = data['WeightBuyMoneySumMean'].values[-20:]
        WeightBuyOrderQtySumMean = data['WeightBuyOrderQtySumMean'].values[-20:]
        WeightSellMoneySumMean = data['WeightSellMoneySumMean'].values[-20:]
        WeightSellOrderQtySumMean = data['WeightSellOrderQtySumMean'].values[-20:]
        close = data['close'].values[-21:]
        
        ret = ts_pct_change(close, 1)[-20:]
        temp_bid_price = WeightBuyMoneySumMean / replace_zero(WeightBuyOrderQtySumMean)
        temp_ask_price = WeightSellMoneySumMean / replace_zero(WeightSellOrderQtySumMean)
        temp_vwap_ratio = temp_ask_price / replace_zero(temp_bid_price) - 1
        factor_init_mask = np.nanquantile(temp_vwap_ratio, 0.5, axis=1, keepdims=True)
        factor_mask_1 = ma.array(ret, mask=(temp_vwap_ratio<=factor_init_mask))
        factor_mask_2 = ma.array(ret, mask=(temp_vwap_ratio>=factor_init_mask))
        factor_raw = np.nanmean(factor_mask_2, axis=1) - np.nanmean(factor_mask_1, axis=1)
        factor = np.nanmean(factor_raw)
        return factor