from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_gp1_future_if(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    # data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Continuous_Data'] = {'IF':['low', 'amount', 'OpenInterest']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        future_low = data['low_cont_IF'].values[-115:]
        future_amount = data['amount_cont_IF'].values[-115:]
        future_position = data['OpenInterest_cont_IF'].values[-115:]
        factor_raw = max2(rolling_norm(future_low, 115), ts_corr(future_amount, future_position, 90))
        return factor_raw[-1]