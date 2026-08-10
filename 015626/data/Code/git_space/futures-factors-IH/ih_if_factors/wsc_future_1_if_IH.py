import numpy as np
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


class wsc_future_1_if_IH(FutureFactor):
    """
    每分钟vwap的5分钟均值与5分钟的vwap之比
    """
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IH':['amount', 'volume']} 
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None    

    def calculate(self, data):
        future_amount = data['amount_cont_IH'].values[-5:]
        future_volume = data['volume_cont_IH'].values[-5:]
        x = np.nanmean(future_amount / future_volume)
        y = np.nansum(future_amount) / np.nansum(future_volume)
        factor = x / y
        return factor
