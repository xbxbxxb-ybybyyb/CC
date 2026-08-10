import numpy as np
import pandas as pd
from future_factor import FutureFactor


class bon_2_to_on_if(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_big_lo_counts', 'sell_big_lo_counts', 'buy_lo_counts', 'sell_lo_counts']
    normalize_size = 1
    normalize_type = 'rolling_norm'

    def calculate(self, df):
        # bon_2_to_on: big_order_number_2 / order_number
        t = 1
        
        bon_2 = df['buy_big_lo_counts'][-t:] + df['sell_big_lo_counts'][-t:]
        on = df['buy_lo_counts'][-t:] + df['sell_lo_counts'][-t:]
        bon_2_to_on = bon_2.sum(axis=1) / on.sum(axis=1)
        
        factor = bon_2_to_on
        factor = factor.values[-1]
        return factor
