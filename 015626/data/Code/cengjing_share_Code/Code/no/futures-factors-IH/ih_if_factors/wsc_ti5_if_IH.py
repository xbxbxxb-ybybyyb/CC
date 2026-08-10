from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_inf



class wsc_ti5_if_IH(FutureFactor):
    data_type = 'Future'
    days_past = 6
    data_dict = dict()
    instrument_type = 'recent'
    # data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Continuous_Data'] = {'IH':['close']}
    normalize_size = 1
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        future_close = data['close_cont_IH'].values[-1321:]
        close_mean = ts_mean(future_close, 40)
        close_std = ts_std(future_close, 40)
        factor_raw = replace_inf(ts_pct_change(close_mean + 2 * close_std, 40))
        factor_mean = ts_rank(factor_raw, 1200)
        return factor_mean[-1]