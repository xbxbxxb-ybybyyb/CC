from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_search5_long_if_IH(FutureFactor):
    data_type = 'Future'
    days_past = 6
    data_dict = dict()
    instrument_type = 'recent'
    # data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Continuous_Data'] = {'IH':['close']}
    normalize_size = 0
    normalize_type = 'rolling_norm'
#    num_range = '(-0.5,1]'
    
    def calculate(self, data):
        future_close = data['close_cont_IH'].values[-1250:]
        factor_raw = rolling_norm(ts_max(ts_delta(future_close, 25), 25), 1200)
        return factor_raw[-1]
