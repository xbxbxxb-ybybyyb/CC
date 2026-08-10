import numpy as np
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


class wsc_spot_8_if_IH(FutureFactor):
    """
    过去10分钟里，沪深300分钟收益率比中证500高的分钟里，沪深300成交额之和
    """
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH':['close', 'amount'], '000905.SH':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        spot_close_if = data['close_000016.SH'].values[-12:]
        spot_close_ic = data['close_000905.SH'].values[-12:]
        spot_amount_if = data['amount_000016.SH'].values[-12:]
        ret_diff = ts_pct_change(spot_close_if, 1) - ts_pct_change(spot_close_ic, 1)
        spot_amount_if[ret_diff < 0] = 0
        factor = np.nanmean(spot_amount_if[-10:])
        return factor
