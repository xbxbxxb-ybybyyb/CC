import numpy as np
import pandas as pd
from future_factor import FutureFactor


class boba_2_to_oba_w_if(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_big_lo_amount', 'buy_lo_amount', 'weight']
    normalize_size = 1
    normalize_type = 'rolling_norm'

    def calculate(self, df):
        # boba_2_to_oba_w: (big_order_buy_amount_2 / order_buy_amount * weight).sum()
        t = 1
        
        boba_2 = df['buy_big_lo_amount'][-t:]
        oba = df['buy_lo_amount'][-t:]
        wt = df['weight'][-t:]
        boba_2_to_oba_w = (boba_2 / oba * wt).sum(axis=1)
        
        factor = boba_2_to_oba_w
        factor = factor.values[-1]
        return factor
