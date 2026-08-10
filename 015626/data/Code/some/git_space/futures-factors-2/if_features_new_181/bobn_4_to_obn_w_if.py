import numpy as np
import pandas as pd
from future_factor import FutureFactor


class bobn_4_to_obn_w_if(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_small_lo_counts', 'buy_lo_counts', 'weight']
    normalize_size = 1
    normalize_type = 'rolling_norm'

    def calculate(self, df):
        # bobn_4_to_obn_w: (big_order_buy_number_4 / order_buy_number * weight).sum()
        t = 1
        
        bobn_4 = df['buy_small_lo_counts'][-t:]
        obn = df['buy_lo_counts'][-t:]
        wt = df['weight'][-t:]
        bobn_4_to_obn_w = (bobn_4 / obn * wt).sum(axis=1)
        
        factor = bobn_4_to_obn_w
        factor = factor.values[-1]
        return factor
