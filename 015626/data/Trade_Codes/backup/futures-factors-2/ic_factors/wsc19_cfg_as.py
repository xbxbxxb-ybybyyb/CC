import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc19_cfg_as(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'amount', 'adjfactor']
    normalize_size = 1000
    normalize_type = 'ts_rank'
#    num_range = '(-0.64,1]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-48:]
        stk_amount = data['amount'].values[-48:]
        n = 30
        arron_up = ts_argmax(stk_close, n) / n * 100  # 过去n分钟最高价出现时间与当前时间的距离占时间段长度的比例
        arron_down = ts_argmin(stk_close, n) / n * 100  # 过去n分钟最低价出现时间与当前时间的距离占时间段长度的比例
        arron_os = arron_up - arron_down
        factor_raw = np.nansum(arron_os * stk_amount, axis=1)
        factor_mean = ts_mean(factor_raw, 18)
        return factor_mean[-1]