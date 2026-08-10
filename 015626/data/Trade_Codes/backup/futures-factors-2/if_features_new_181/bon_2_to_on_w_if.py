import numpy as np
import pandas as pd
from future_factor import FutureFactor


class bon_2_to_on_w_if(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_big_lo_counts', 'sell_big_lo_counts', 'buy_lo_counts', 'sell_lo_counts', 'weight']
    normalize_size = 1
    normalize_type = 'rolling_norm'

    def calculate(self, df):
        # bon_2_to_on_w: (big_order_number_2 / order_number * weight).sum()
        t = 1
        
        bon_2 = df['buy_big_lo_counts'][-t:] + df['sell_big_lo_counts'][-t:]
        on = df['buy_lo_counts'][-t:] + df['sell_lo_counts'][-t:]
        wt = df['weight'][-t:]
        bon_2_to_on_w = (bon_2 / on * wt).sum(axis=1)
        
        factor = bon_2_to_on_w
        factor = factor.values[-1]
        return factor
