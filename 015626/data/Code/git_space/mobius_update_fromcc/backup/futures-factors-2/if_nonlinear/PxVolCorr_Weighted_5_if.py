import numpy as np
from operators_cc import *
from future_factor import FutureFactor


class PxVolCorr_Weighted_5_if(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight', 'PxVolCorr']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        PxVolCorr = data['PxVolCorr'].iloc[-5:]
        weight = data['weight'].values[-1]
        
        date = str(PxVolCorr.index[-1].date())
        PxVolCorr = PxVolCorr.loc[date].values
        a = cross_if(PxVolCorr)
        if a.shape[0] > 1:
            a = np.nanmean(a, axis=0)
        factor = np.nanmean(a * weight)
        
        return factor
