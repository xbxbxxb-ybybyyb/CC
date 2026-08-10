import numpy as np
from future_factor import FutureFactor


class wsc_search1_long_IH(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH':['close']}
    normalize_size = 600
    normalize_type = 'rolling_norm'
#    num_range = '(-0.5,1]'
    
    def calculate(self, data):
        spot_close = data['close_000016.SH'].values[-45:]
        reg_x = np.arange(45) + 1.
        spot_close_centralized = spot_close - np.nanmean(spot_close)
        reg_x_centralized = reg_x - np.nanmean(reg_x)
        factor_raw = np.nansum(spot_close_centralized*reg_x_centralized) / np.nansum(reg_x_centralized**2)
        return factor_raw
