from future_factor import FutureFactor
from operators_wsc_1_0 import *
    

class wsc4_future_kpz_IH(FutureFactor):
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
        future_close = data['close_cont_IH'].values[-1322:]
        N = 20
        dpo = future_close - ts_delay(ts_mean(future_close, N), int(N/2+1))
        factor_init = abs(dpo - ts_median(dpo, 60))
        factor_mean = ts_mean(factor_init, 30)
        factor_raw = ts_rank(factor_mean, 1200)
        return factor_raw[-1]
