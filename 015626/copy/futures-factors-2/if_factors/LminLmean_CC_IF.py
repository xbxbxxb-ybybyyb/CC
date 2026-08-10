import bottleneck as bk
from future_factor import FutureFactor


class LminLmean_CC_IF(FutureFactor):

    data_type = 'Future' 
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IF':['low']}
    normalize_size = 484
    normalize_type = 'rolling_norm' 

    
    def calculate(self, data):
        future_low = data['low_cont_IF'].values[-90:]
        
        ctl_r = -bk.move_min(future_low, 90, 15) / bk.move_mean(future_low, 15, 5)
        return ctl_r[-1]