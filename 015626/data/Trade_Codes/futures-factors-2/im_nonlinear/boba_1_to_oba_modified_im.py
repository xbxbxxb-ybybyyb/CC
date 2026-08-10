import numpy as np
import pandas as pd
from future_factor import FutureFactor


class boba_1_to_oba_modified_im(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_super_lo_amount', 'buy_lo_amount']
    normalize_size = 1
    normalize_type = 'rolling_norm'

    def calculate(self, df):
        # boba_1_to_oba: big_order_buy_amount_1 / order_buy_amount
        t = 1
        
        boba_1 = df['buy_super_lo_amount'][-t:]
        oba = df['buy_lo_amount'][-t:]
        boba_1_to_oba = boba_1.sum(axis=1) / oba.sum(axis=1)
        
        factor = boba_1_to_oba
        factor = factor.values[-1]
        return np.log(factor) if factor > 0 else np.nan
