import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

class PositiontoVolume_CC(FutureFactor):

    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['OpenInterest','volume']} 
    normalize_size = 1200
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    handle_preadj = None 
    
    def calculate(self, data):
        a = data['volume_cont_IC'][-41:].rolling(40, min_periods = 30).std()
        a[abs(a) < 1e-8] = np.nan
        pd_r = -1 * data['OpenInterest_cont_IC'][-41:]/ a
        factor = pd_r.values[-1]
        return factor