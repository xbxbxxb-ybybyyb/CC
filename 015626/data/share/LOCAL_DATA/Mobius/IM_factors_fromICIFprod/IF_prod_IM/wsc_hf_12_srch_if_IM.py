import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero, rolling_window_upgrade


def ts_position(data, d):
    if not isinstance(data, np.ndarray):
        data = data.values
    data_expanding = rolling_window_upgrade(data, d)
    output_need = (data_expanding[..., -1] - np.nanmin(data_expanding, axis=-1)) / (
            np.nanmax(data_expanding, axis=-1) - np.nanmin(data_expanding, axis=-1))
    output = np.full(data.shape, np.nan)
    output[d - 1:] = output_need
    return output

    
class wsc_hf_12_srch_if_IM(FutureFactor):

    """
    -ts_position(bun_r + ts_max(bun_r, 10) + bun_to_bn_w, 100)
    """
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'SellUniqueOrderNum', 'weight', 'BuyTradeNum']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy_unique_num = data['BuyUniqueOrderNum'].values[-115:]
        sell_unique_num = data['SellUniqueOrderNum'].values[-115:]
        buy_trade_num = data['BuyTradeNum'].values[-115:]
        stk_weight = data['weight'].values[-115:]
        
        bun = np.nansum(buy_unique_num, axis=1)
        sun = np.nansum(sell_unique_num, axis=1)
        bun_r = bun / (bun + sun)
        bun_to_bn_w = np.nansum(buy_unique_num / replace_zero(buy_trade_num) * stk_weight, axis=1)

        factor_raw = -ts_position(bun_r + ts_max(bun_r, 10) + bun_to_bn_w, 100)
        factor = np.nanmean(factor_raw[-5:])
        return factor