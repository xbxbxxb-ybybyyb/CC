import numpy as np
import pandas as pd
from future_factor import FutureFactor


class bon_1_to_on_if(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_super_lo_counts', 'sell_super_lo_counts', 'buy_lo_counts', 'sell_lo_counts']
    normalize_size = 1
    normalize_type = 'rolling_norm'

    def calculate(self, df):
        # bon_1_to_on: big_order_number_1 / order_number
        t = 1
        
        bon_1 = df['buy_super_lo_counts'][-t:] + df['sell_super_lo_counts'][-t:]
        on = df['buy_lo_counts'][-t:] + df['sell_lo_counts'][-t:]
        bon_1_to_on = bon_1.sum(axis=1) / on.sum(axis=1)
        
        factor = bon_1_to_on
        factor = factor.values[-1]
        return factor
