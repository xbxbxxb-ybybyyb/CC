from operators_wsc_1_0 import *
from future_factor import FutureFactor


class wsc4_spot_kpz_if(FutureFactor):

    data_type = 'Future' 
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    
    
    def calculate(self, data):
        spot_close = data['close_000905.SH'].values[-122:]
        
        N = 20
        dpo = spot_close - ts_delay(ts_mean(spot_close, N), int(N/2+1))
        factor_raw = abs(dpo - ts_median(dpo, 60))
        factor_mean = ts_mean(factor_raw, 30)
        return factor_mean[-1]
    