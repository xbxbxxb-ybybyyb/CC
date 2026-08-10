from future_factor import FutureFactor
import pandas as pd
import numpy as np
import bottleneck as bk

class wyc_ts107_vwap_fu_IF(FutureFactor):
    
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['volume', 'amount']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        N = 10
        volume = data['volume_cont_IF'][-N:].values
        amount = data['amount_cont_IF'][-N:].values
        vwap = amount / volume
        f = np.nanmean(vwap) / (np.nansum(amount) / np.nansum(volume))
        if np.isinf(f):
            return np.nan
        return f 