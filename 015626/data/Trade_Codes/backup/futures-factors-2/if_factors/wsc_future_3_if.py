import numpy as np
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


class wsc_future_3_if(FutureFactor):
    """
    IF合约10分钟amount和用high、low估计出来的成交额之差
    """
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IF':['high', 'low', 'amount', 'volume']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        future_high = data['high_cont_IF'].values[-10:]
        future_low = data['low_cont_IF'].values[-10:]
        future_amount = data['amount_cont_IF'].values[-10:]
        future_volume = data['volume_cont_IF'].values[-10:]
        
        n = 10
        factor_raw = ((future_high + future_low) / 2 * future_volume * 300 - future_amount)
        factor = np.nanmean(factor_raw[-n:])
        return factor
