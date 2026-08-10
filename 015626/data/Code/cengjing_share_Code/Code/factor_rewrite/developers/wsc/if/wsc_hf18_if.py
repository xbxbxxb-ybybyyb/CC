import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero


    
class wsc_hf18_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['Buy1NumOrdersMean', 'Bid1AmtMean', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_Buy1NumOrdersMean = data['Buy1NumOrdersMean'].values[-20:]
        stk_Bid1AmtMean = data['Bid1AmtMean'].values[-20:]
        stk_weight = data['weight'].values[-20:]
        factor_raw = np.nansum(stk_Bid1AmtMean / replace_zero(stk_Buy1NumOrdersMean) * stk_weight, axis=1)
        factor_mean = ts_mean(factor_raw, 20)
        return factor_mean[-1]