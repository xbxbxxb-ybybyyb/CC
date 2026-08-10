import numpy as np
import pandas as pd
from future_factor import FutureFactor
from operators_wsc_for_srch import *


class wsc_hf_1_srch_ihbyif_if(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [
        'buy_smallorder_money',
        'sell_smallorder_money_v2',
        'BuyTradeMoney',
        'weight',
    ]
    normalize_size = 1200
    normalize_type = 'ts_rank'

    def calculate(self, df):
        # -(df['bba_4_r'] + df['bba_4_to_ba_w'] + up_down_ratio(ts_pred(df['bba_4_r'], 30), 100, 10))
        t = 200
        
        bba_4 = df['buy_smallorder_money'][-t:]
        sba_4 = df['sell_smallorder_money_v2'][-t:]
        bba_4_r = bba_4.sum(axis=1) / (bba_4.sum(axis=1) + sba_4.sum(axis=1))
        
        ba = df['BuyTradeMoney'][-t:]
        wt = df['weight'][-t:]
        bba_4_to_ba_w = (bba_4 / ba * wt).sum(axis=1)

        factor = -(bba_4_r + bba_4_to_ba_w + up_down_ratio(ts_pred(bba_4_r, 30), 100, 10))
        factor = factor.values[-1]
        return factor
