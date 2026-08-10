import numpy as np
import pandas as pd
from future_factor import FutureFactor


class boa_2_to_oa_if(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_big_lo_amount', 'sell_big_lo_amount', 'buy_lo_amount', 'sell_lo_amount']
    normalize_size = 1
    normalize_type = 'rolling_norm'

    def calculate(self, df):
        # boa_2_to_oa: big_order_amount_2 / order_amount
        t = 1
        
        boa_2 = df['buy_big_lo_amount'][-t:] + df['sell_big_lo_amount'][-t:]
        oa = df['buy_lo_amount'][-t:] + df['sell_lo_amount'][-t:]
        boa_2_to_oa = boa_2.sum(axis=1) / oa.sum(axis=1)
        
        factor = boa_2_to_oa
        factor = factor.values[-1]
        return factor
