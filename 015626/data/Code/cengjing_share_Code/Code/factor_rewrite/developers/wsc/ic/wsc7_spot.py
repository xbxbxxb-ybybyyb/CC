import numpy as np
from future_factor import FutureFactor

    
class wsc7_spot(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1150
    normalize_type = 'ts_rank'
    num_range = '(-0.5,1]'
    
    def calculate(self, data):
        spot_amount = data['amount_000905.SH'].values[-20:]
        return np.nanmax(spot_amount)
