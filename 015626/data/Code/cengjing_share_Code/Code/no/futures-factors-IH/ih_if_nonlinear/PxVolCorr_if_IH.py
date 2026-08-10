import numpy as np
from operators_cc import *
from future_factor import FutureFactor


class PxVolCorr_if_IH(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['PxVolCorr']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        PxVolCorr = data['PxVolCorr'].values[-1]

        a = cross_if(PxVolCorr)
        factor = np.nanmean(a)
        
        return factor
