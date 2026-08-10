from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_gp4_future(FutureFactor):
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
        future_amount = data['amount_cont_IC'].values[-103:]
        amount_max = ts_max(future_amount, 39)
        factor_raw = ts_pred(amount_max, 64)
        return factor_raw[-1]