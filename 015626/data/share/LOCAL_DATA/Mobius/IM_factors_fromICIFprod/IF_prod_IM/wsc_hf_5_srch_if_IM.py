import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero


class wsc_hf_5_srch_if_IM(FutureFactor):

    """
    -midprice(ts_ratio_from_mean(ts_reg_alpha(sic_w, 59), 70), bun_r, 15)
    """
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'SellUniqueOrderNum', 'stk_index_corr_zz1000', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False

    def calculate(self, data):
        buy_unique_num = data['BuyUniqueOrderNum'].values[-145:]
        sell_unique_num = data['SellUniqueOrderNum'].values[-145:]
        stk_index_corr = data['stk_index_corr_zz1000'].values[-145:]
        stk_weight = data['weight'].values[-145:]

        factor_init_1 = np.nansum(buy_unique_num, axis=1)
        factor_init_2 = np.nansum(sell_unique_num, axis=1)
        bun_r = factor_init_1 / (factor_init_1 + factor_init_2)
        sic_w = np.nansum(stk_index_corr * stk_weight, axis=1)
        
        factor_init = ts_reg_alpha(sic_w, 59)
        factor_raw = factor_init / replace_zero(ts_mean(factor_init, 70))
        factor = -(np.nanmax(factor_raw[-15:]) + np.nanmin(bun_r[-15:]))
        return factor