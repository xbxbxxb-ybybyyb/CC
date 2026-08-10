import numpy as np
import pandas as pd
from future_factor import FutureFactor
from operators_wsc_for_srch import *


class cf_search4_if(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [
        'close',
        'amount',
        'buy_smallorder_money',
        'sell_smallorder_money_v2',
    ]
    normalize_size = 1200
    normalize_type = 'ts_rank'

    def calculate(self, df):
        # ts_min(sub2(midpoint(ra_corr, 70), bba_4_r), 10)
        t = 140
        
        close = df['close'][-t:]
        amount = df['amount'][-t:]
        ret_1min = close.diff(1) / close.shift(1)
        ra_corr = ret_1min.corrwith(amount, axis=1)
        
        bba_4 = df['buy_smallorder_money'][-t:]
        sba_4 = df['sell_smallorder_money_v2'][-t:]
        bba_4_r = bba_4.sum(axis=1) / (bba_4.sum(axis=1) + sba_4.sum(axis=1))

        factor = ts_min(sub2(midpoint(ra_corr, 70), bba_4_r), 10)
        factor = factor.values[-1]
        return factor
