import bottleneck as bk
from operators_cc import *
from future_factor import FutureFactor

class LminLmean_ICIF_CC_IF_IH(FutureFactor):

    data_type = 'Future' 
    days_past = 3
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IH':['low']}
    normalize_size = 484
    normalize_type = 'rolling_norm' 
    
    
    def calculate(self, data):
        future_low = data['low_cont_IH'].values[-549:]
        
        ctl_r = -bk.move_min(future_low, 60, 15) / bk.move_mean(future_low, 15, 5)
        factor = rolling_norm(ctl_r, 484)
        factor = bk.move_mean(factor, 5, 3)
        return factor[-1]