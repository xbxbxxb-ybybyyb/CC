import numpy as np
import pandas as pd
from future_factor import FutureFactor


class boa_3_to_oa_im(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_mid_lo_amount', 'sell_mid_lo_amount', 'buy_lo_amount', 'sell_lo_amount']
    normalize_size = 1
    normalize_type = 'rolling_norm'

    def calculate(self, df):
        # boa_3_to_oa: big_order_amount_3 / order_amount
        t = 1
        
        boa_3 = df['buy_mid_lo_amount'][-t:] + df['sell_mid_lo_amount'][-t:]
        oa = df['buy_lo_amount'][-t:] + df['sell_lo_amount'][-t:]
        boa_3_to_oa = boa_3.sum(axis=1) / oa.sum(axis=1)
        
        factor = boa_3_to_oa
        factor = factor.values[-1]
        return factor
