import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

class VwRetSk_CC(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['vwap']}
    normalize_size = 1200
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    handle_preadj = None 
    
    def calculate(self, data):
        vsk_r = data['vwap_cont_IC'][-31:].diff()
        factor = -1 * vsk_r.rolling(30, min_periods = 15).skew().values[-1]       
        return factor