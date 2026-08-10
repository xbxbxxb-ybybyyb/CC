import numpy as np
import pandas as pd
from future_factor import FutureFactor


class bobn_2_to_obn_w_ic(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_big_lo_counts', 'buy_lo_counts', 'weight']
    normalize_size = 1
    normalize_type = 'rolling_norm'

    def calculate(self, df):
        # bobn_2_to_obn_w: (big_order_buy_number_2 / order_buy_number * weight).sum()
        t = 1
        
        bobn_2 = df['buy_big_lo_counts'][-t:]
        obn = df['buy_lo_counts'][-t:]
        wt = df['weight'][-t:]
        bobn_2_to_obn_w = (bobn_2 / obn * wt).sum(axis=1)
        
        factor = bobn_2_to_obn_w
        factor = factor.values[-1]
        return factor
