from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_gp8_future(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    # data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Continuous_Data'] = {'IC':['amount']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        future_amount = data['amount_cont_IC'].iloc[-105:]
        amount_std = ts_std(future_amount, 68)
        factor_raw = ts_reg_beta(amount_std, 37)
        return factor_raw[-1]