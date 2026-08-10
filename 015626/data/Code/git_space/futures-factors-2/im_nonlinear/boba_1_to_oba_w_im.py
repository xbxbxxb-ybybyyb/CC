import numpy as np
import pandas as pd
from future_factor import FutureFactor


class boba_1_to_oba_w_im(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_super_lo_amount', 'buy_lo_amount', 'weight']
    normalize_size = 1
    normalize_type = 'rolling_norm'

    def calculate(self, df):
        # boba_1_to_oba_w: (big_order_buy_amount_1 / order_buy_amount * weight).sum()
        t = 1
        
        boba_1 = df['buy_super_lo_amount'][-t:]
        oba = df['buy_lo_amount'][-t:]
        wt = df['weight'][-t:]
        boba_1_to_oba_w = (boba_1 / oba * wt).sum(axis=1)
        
        factor = boba_1_to_oba_w
        factor = factor.values[-1]
        return factor
