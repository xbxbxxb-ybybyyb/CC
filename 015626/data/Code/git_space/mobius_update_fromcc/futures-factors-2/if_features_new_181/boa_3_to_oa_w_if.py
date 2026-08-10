import numpy as np
import pandas as pd
from future_factor import FutureFactor


class boa_3_to_oa_w_if(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_mid_lo_amount', 'sell_mid_lo_amount', 'buy_lo_amount', 'sell_lo_amount', 'weight']
    normalize_size = 1
    normalize_type = 'rolling_norm'

    def calculate(self, df):
        # boa_3_to_oa_w: (big_order_amount_3 / order_amount * weight).sum()
        t = 1
        
        boa_3 = df['buy_mid_lo_amount'][-t:] + df['sell_mid_lo_amount'][-t:]
        oa = df['buy_lo_amount'][-t:] + df['sell_lo_amount'][-t:]
        wt = df['weight'][-t:]
        boa_3_to_oa_w = (boa_3 / oa * wt).sum(axis=1)
        
        factor = boa_3_to_oa_w
        factor = factor.values[-1]
        return factor
