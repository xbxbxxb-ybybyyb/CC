import numpy as np
import pandas as pd
from future_factor import FutureFactor


class boa_1_to_oa_ic(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_super_lo_amount', 'sell_super_lo_amount', 'buy_lo_amount', 'sell_lo_amount']
    normalize_size = 1
    normalize_type = 'rolling_norm'

    def calculate(self, df):
        # boa_1_to_oa: big_order_amount_1 / order_amount
        t = 1
        
        boa_1 = df['buy_super_lo_amount'][-t:] + df['sell_super_lo_amount'][-t:]
        oa = df['buy_lo_amount'][-t:] + df['sell_lo_amount'][-t:]
        boa_1_to_oa = boa_1.sum(axis=1) / oa.sum(axis=1)
        
        factor = boa_1_to_oa
        factor = factor.values[-1]
        return factor
