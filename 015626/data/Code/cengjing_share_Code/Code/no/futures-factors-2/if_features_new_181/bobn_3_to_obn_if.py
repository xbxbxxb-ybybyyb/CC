import numpy as np
import pandas as pd
from future_factor import FutureFactor


class bobn_3_to_obn_if(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_mid_lo_counts', 'buy_lo_counts']
    normalize_size = 1
    normalize_type = 'rolling_norm'

    def calculate(self, df):
        # bobn_3_to_obn: big_order_buy_number_3 / order_buy_number
        t = 1
        
        bobn_3 = df['buy_mid_lo_counts'][-t:]
        obn = df['buy_lo_counts'][-t:]
        bobn_3_to_obn = bobn_3.sum(axis=1) / obn.sum(axis=1)
        
        factor = bobn_3_to_obn
        factor = factor.values[-1]
        return factor
