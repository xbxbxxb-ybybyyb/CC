import bottleneck as bk
from future_factor import FutureFactor

class LminLmean_CC_IF(FutureFactor):

    data_type = 'Future' 
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IF':['low']}
    normalize_size = 1000
    normalize_type = 'ts_rank' 
 
    def calculate(self, data):
        future_low = data['low_cont_IF'].values[-20:]
        ctl_r = -np.min(future_low) / np.nanmean(future_low)
        return ctl_r