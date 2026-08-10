from future_factor import FutureFactor
from operators_wsc_1_0 import *


class wsc2_spot_IH(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH':['close']}
    normalize_size = 380
    normalize_type = 'rolling_norm'
#    num_range = '[0,1]'
    
    def calculate(self, data):
        spot_close = data['close_000016.SH'].values[-85:]
        close_ma_long = ts_mean(spot_close, 85)
        close_ma_short = ts_mean(spot_close, 10)
        factor_raw = close_ma_short - close_ma_long
        return factor_raw[-1]