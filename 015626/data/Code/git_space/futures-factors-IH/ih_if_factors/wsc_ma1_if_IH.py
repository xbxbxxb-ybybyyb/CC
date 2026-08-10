from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_ma1_if_IH(FutureFactor):
    data_type = 'Future'
    days_past = 3
    data_dict = dict()
    instrument_type = 'recent'
    # data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Continuous_Data'] = {'IH':['close']}
    normalize_size = 0
    normalize_type = 'rolling_norm'
    num_range = None
    
    def calculate(self, data):
        future_close = data['close_cont_IH'].values[-480:]
        close_ma_long = ts_mean(future_close, 120)
        close_ma_short = ts_mean(future_close, 15)
        factor_raw = rolling_norm(close_ma_short-close_ma_long, 360)
        return factor_raw[-1]
