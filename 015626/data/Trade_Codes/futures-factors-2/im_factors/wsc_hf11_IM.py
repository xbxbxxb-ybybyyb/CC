import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero, replace_inf




class wsc_hf11_IM(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'SellTradeMoney']
    normalize_size = 900
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        stk_close = replace_zero(data['close'].values[-37:])
        stk_SellTradeMoney = data['SellTradeMoney'].iloc[-37:].fillna(0).values  # fillna是因为之前研究用的数据是这么处理的
        stk_ret = replace_inf(ts_pct_change(stk_close, 1))
        # x = (stk_SellTradeMoney.rank(axis=1, pct=True) * 2 - 1).values
        x = section_rank_np(stk_SellTradeMoney, pct=True) * 2 - 1
        factor_init = np.nansum(x*stk_ret, axis=1)
        factor_raw = ts_mean(factor_init, 36)
        return factor_raw[-1]