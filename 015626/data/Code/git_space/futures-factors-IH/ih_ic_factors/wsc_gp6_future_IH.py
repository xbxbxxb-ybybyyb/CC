from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_gp6_future_IH(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    # data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Continuous_Data'] = {'IH':['volume']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        future_volume = data['volume_cont_IH'].iloc[-22:]
        factor_raw = ts_std(future_volume, 22)
        return factor_raw[-1]