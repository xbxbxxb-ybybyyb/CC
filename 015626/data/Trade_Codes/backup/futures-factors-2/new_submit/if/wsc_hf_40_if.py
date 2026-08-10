import numpy as np
import numpy.ma as ma
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_40_if(FutureFactor):
    # 用ts_sharpe盘口卖单金额/盘口卖单金额, 60)来衡量盘口买卖压，这个因子是卖压越大的股票的平均收益率越高越好

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['WeightBuyMoneySumMean', 'WeightSellMoneySumMean', 'close']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        WeightBuyMoneySumMean = data['WeightBuyMoneySumMean'].values[-180:]
        WeightSellMoneySumMean = data['WeightSellMoneySumMean'].values[-180:]
        close = data['close'].values[-122:]
        
        stk_ret_1 = ts_pct_change(close, 1)[-120:]
        temp_a = WeightBuyMoneySumMean / replace_zero(WeightSellMoneySumMean)
        factor_init = (ts_mean(temp_a, 60) / ts_std(temp_a, 60))[-120:]
        factor_init_mask = np.nanquantile(factor_init, 0.5, axis=1, keepdims=True)
        factor_mask_1 = ma.array(stk_ret_1, mask=(factor_init<=factor_init_mask))
        factor_mask_2 = ma.array(stk_ret_1, mask=(factor_init>=factor_init_mask))
        factor_raw = np.nanmean(factor_mask_2, axis=1) - np.nanmean(factor_mask_1, axis=1)
        factor = np.nanmean(factor_raw)
        return factor