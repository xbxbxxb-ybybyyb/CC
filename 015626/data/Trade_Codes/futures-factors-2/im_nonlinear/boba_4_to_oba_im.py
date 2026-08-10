import numpy as np
import pandas as pd
from future_factor import FutureFactor


class boba_4_to_oba_im(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_small_lo_amount', 'buy_lo_amount']
    normalize_size = 1
    normalize_type = 'rolling_norm'

    def calculate(self, df):
        # boba_4_to_oba: big_order_buy_amount_4 / order_buy_amount
        t = 1
        
        boba_4 = df['buy_small_lo_amount'][-t:]
        oba = df['buy_lo_amount'][-t:]
        boba_4_to_oba = boba_4.sum(axis=1) / oba.sum(axis=1)
        
        factor = boba_4_to_oba
        factor = factor.values[-1]
        return factor
