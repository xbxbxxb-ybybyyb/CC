import numpy as np
import pandas as pd
from future_factor import FutureFactor
from operators_wsc_for_srch import *


class cf_search8_if(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [
        'buy_superorder_money',
        'BuyTradeMoney',
        'buy_smallorder_money',
        'sell_smallorder_money_v2',
    ]
    normalize_size = 1200
    normalize_type = 'ts_rank'

    def calculate(self, df):
        # -add2(coefficient_of_variation(bba_1_to_ba, 45), midpoint(bba_4_r, 15))
        t = 90
        
        bba_1 = df['buy_superorder_money'][-t:]
        ba = df['BuyTradeMoney'][-t:]
        bba_1_to_ba = bba_1.sum(axis=1) / ba.sum(axis=1)

        bba_4 = df['buy_smallorder_money'][-t:]
        sba_4 = df['sell_smallorder_money_v2'][-t:]
        bba_4_r = bba_4.sum(axis=1) / (bba_4.sum(axis=1) + sba_4.sum(axis=1))

        factor = -add2(coefficient_of_variation(bba_1_to_ba, 45), midpoint(bba_4_r, 15))
        factor = factor.values[-1]
        return factor
