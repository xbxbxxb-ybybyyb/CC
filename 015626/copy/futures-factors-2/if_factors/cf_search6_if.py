import numpy as np
import pandas as pd
from future_factor import FutureFactor
from operators_wsc_for_srch import *


class cf_search6_if(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [
        'buy_bigorder_money',
        'sell_bigorder_money_v2',
        'sell_superorder_count_v2',
        'SellUniqueOrderNum',
        'BuyUniqueOrderNum',
        'weight',
    ]
    normalize_size = 1200
    normalize_type = 'ts_rank'

    def calculate(self, df):
        # sub2(sigmoid(ts_corr(bba_2_r_w, ts_pct_change(sbn_1_to_sun_w, 90), 80)), midpoint(bun_r, 15))
        t = 180
        
        bba_2 = df['buy_bigorder_money'][-t:]
        sba_2 = df['sell_bigorder_money_v2'][-t:]
        wt = df['weight'][-t:]
        bba_2_r_w = ((bba_2 / (bba_2 + sba_2)) * wt).sum(axis=1)

        sbn_1 = df['sell_superorder_count_v2'][-t:]
        sun = sun = df['SellUniqueOrderNum'][-t:]
        sbn_1_to_sun_w = (sbn_1 / sun * wt).sum(axis=1)

        bun = df['BuyUniqueOrderNum'][-t:]
        bun_r = bun.sum(axis=1) / (bun.sum(axis=1) + sun.sum(axis=1))

        factor = sub2(sigmoid(ts_corr(bba_2_r_w, ts_pct_change(sbn_1_to_sun_w, 90), 80)), midpoint(bun_r, 15))
        factor = factor.values[-1]
        return factor
