import numpy as np
import pandas as pd
from future_factor import FutureFactor


class bobn_1_to_obn_modified_if(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_super_lo_counts', 'buy_lo_counts']
    normalize_size = 1
    normalize_type = 'rolling_norm'

    def calculate(self, df):
        # bobn_1_to_obn: big_order_buy_number_1 / order_buy_number
        t = 1
        
        bobn_1 = df['buy_super_lo_counts'][-t:]
        obn = df['buy_lo_counts'][-t:]
        bobn_1_to_obn = bobn_1.sum(axis=1) / obn.sum(axis=1)
        
        factor = bobn_1_to_obn
        factor = factor.values[-1]
        return np.log(factor) if factor > 0 else np.nan
