from future_factor import FutureFactor
from operators_wsc_1_0 import *


class wsc1_future_kpz_IH(FutureFactor):
    data_type = 'Future'
    days_past = 2
    data_dict = dict()
    instrument_type = 'recent'
    # data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Continuous_Data'] = {'IH':['close']}
    normalize_size = 0
    normalize_type = 'rolling_norm'
#    num_range = '[0,1]'
    
    def calculate(self, data):
        future_close = data['close_cont_IH'].values[-240:]
        factor_init = log(future_close)
        factor_raw = rolling_norm(factor_init, 240)
        return factor_raw[-1]



