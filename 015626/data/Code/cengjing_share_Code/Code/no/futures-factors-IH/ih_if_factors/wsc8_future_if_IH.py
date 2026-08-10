from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc8_future_if_IH(FutureFactor):
    data_type = 'Future'
    days_past = 10
    data_dict = dict()
    instrument_type = 'recent'
    # data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Continuous_Data'] = {'IH':['close', 'high', 'low']}
    normalize_size = 1
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        future_close = data['close_cont_IH'].iloc[-2170:]
        future_high = data['high_cont_IH'].iloc[-2170:]
        future_low = data['low_cont_IH'].iloc[-2170:]
        n = 30
        m = 80
        low_n = ts_min(future_low, n)
        high_n = ts_max(future_high, n)
        a = high_n - low_n
        b = (future_close - low_n) / replace_zero(a)
        b_low = ts_min(b, m)
        b_high = ts_max(b, m)
        c = b_high - b_low
        d = (b - b_low) / replace_zero(c)
        e = ts_truncated_ema(d, d=60, alpha=2/3)
        factor_init = ts_truncated_ema(e, d=60, alpha=2/3)
        factor_mean = ts_mean(factor_init, 140)
        factor_raw = ts_rank(factor_mean, 1800)
        return factor_raw[-1]
