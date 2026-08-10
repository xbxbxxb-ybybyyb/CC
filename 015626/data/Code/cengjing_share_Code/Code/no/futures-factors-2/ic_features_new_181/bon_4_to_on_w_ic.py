import numpy as np
import pandas as pd
from future_factor import FutureFactor


class bon_4_to_on_w_ic(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_small_lo_counts', 'sell_small_lo_counts', 'buy_lo_counts', 'sell_lo_counts', 'weight']
    normalize_size = 1
    normalize_type = 'rolling_norm'

    def calculate(self, df):
        # bon_4_to_on_w: (big_order_number_4 / order_number * weight).sum()
        t = 1
        
        bon_4 = df['buy_small_lo_counts'][-t:] + df['sell_small_lo_counts'][-t:]
        on = df['buy_lo_counts'][-t:] + df['sell_lo_counts'][-t:]
        wt = df['weight'][-t:]
        bon_4_to_on_w = (bon_4 / on * wt).sum(axis=1)
        
        factor = bon_4_to_on_w
        factor = factor.values[-1]
        return factor
