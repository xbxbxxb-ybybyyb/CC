import numpy as np
import pandas as pd
from future_factor import FutureFactor
from operators_wsc_for_srch import *


class cf_search7_if(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [
        'buy_midorder_money',
        'sell_midorder_money_v2',
        'BuyUniqueOrderNum',
        'BuyTradeNum',
        'buy_smallorder_money',
        'sell_smallorder_money_v2',
        'weight',
    ]
    normalize_size = 1200
    normalize_type = 'ts_rank'

    def calculate(self, df):
        # -midprice(up_down_ratio(midprice(bba_3_r, bun_to_bn_w, 25), 90, 20), bba_4_r, 10)
        t = 180
        
        bba_3 = df['buy_midorder_money'][-t:]
        sba_3 = df['sell_midorder_money_v2'][-t:]
        bba_3_r = bba_3.sum(axis=1) / (bba_3.sum(axis=1) + sba_3.sum(axis=1))

        bun = df['BuyUniqueOrderNum'][-t:]
        bn = df['BuyTradeNum'][-t:]
        wt = df['weight'][-t:]
        bun_to_bn_w = (bun / bn * wt).sum(axis=1)

        bba_4 = df['buy_smallorder_money'][-t:]
        sba_4 = df['sell_smallorder_money_v2'][-t:]
        bba_4_r = bba_4.sum(axis=1) / (bba_4.sum(axis=1) + sba_4.sum(axis=1))

        factor = -midprice(up_down_ratio(midprice(bba_3_r, bun_to_bn_w, 25), 90, 20), bba_4_r, 10)
        factor = factor.values[-1]
        return factor
