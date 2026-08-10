import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *


    
class wsc_hf17(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['Bid1AmtMean', 'Buy1NumOrdersMean']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        stk_Bid1AmtMean = data['Bid1AmtMean'].values[-1]
        stk_Buy1NumOrdersMean = data['Buy1NumOrdersMean'].values[-1]
        factor_raw = np.nansum(stk_Bid1AmtMean) / np.nansum(stk_Buy1NumOrdersMean)
        return factor_raw