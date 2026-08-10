import numpy as np
import pandas as pd
from future_factor import FutureFactor
from operators_wsc_for_srch import *


class cf_search22_byif_ih_if(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [
        'buy_bigorder_money',
        'BuyTradeMoney',
        'sell_midorder_money_v2',
        'SellTradeMoney',
        'buy_smallorder_money',
        'sell_smallorder_money_v2',
        'weight',
    ]
    normalize_size = 1200
    normalize_type = 'ts_rank'

    def calculate(self, df):
        # -midprice(up_down_ratio(ts_cov(df['bba_2_to_ba_w'], df['sba_3_to_sa'], 65), 105, 10), df['bba_4_r'], 15)
        t = 210
        
        bba_2 = df['buy_bigorder_money'][-t:]
        ba = df['BuyTradeMoney'][-t:]
        wt = df['weight'][-t:]
        bba_2_to_ba_w = (bba_2 / ba * wt).sum(axis=1)
        
        sba_3 = df['sell_midorder_money_v2'][-t:]
        sa = df['SellTradeMoney'][-t:]
        sba_3_to_sa = sba_3.sum(axis=1) / sa.sum(axis=1)
        
        bba_4 = df['buy_smallorder_money'][-t:]
        sba_4 = df['sell_smallorder_money_v2'][-t:]
        bba_4_r = bba_4.sum(axis=1) / (bba_4.sum(axis=1) + sba_4.sum(axis=1))

        factor = -midprice(up_down_ratio(ts_cov(bba_2_to_ba_w, sba_3_to_sa, 65), 105, 10), bba_4_r, 15)
        factor = factor.values[-1]
        return factor
        