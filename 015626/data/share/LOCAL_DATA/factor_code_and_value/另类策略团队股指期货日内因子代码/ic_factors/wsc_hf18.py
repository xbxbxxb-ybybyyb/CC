import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero


    
class wsc_hf18(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['Bid1AmtMean', 'Buy1NumOrdersMean', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        stk_weight = data['weight'].values[-15:]
        stk_Bid1AmtMean = data['Bid1AmtMean'].values[-15:]
        stk_Buy1NumOrdersMean = data['Buy1NumOrdersMean'].values[-15:]
        factor_init = np.nansum(stk_Bid1AmtMean / replace_zero(stk_Buy1NumOrdersMean) * stk_weight, axis=1)
        factor_raw = ts_mean(factor_init, 15)
        return factor_raw[-1]