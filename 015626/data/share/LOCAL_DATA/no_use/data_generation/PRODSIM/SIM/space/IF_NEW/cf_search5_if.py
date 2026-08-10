import numpy as np
import pandas as pd
from future_factor import FutureFactor
from operators_wsc_for_srch import *


class cf_search5_if(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [
        'buy_smallorder_money',
        'sell_smallorder_money_v2',
        'BuyUniqueOrderNum',
        'BuyTradeNum',
        'weight',
    ]
    normalize_size = 1200
    normalize_type = 'ts_rank'

    def calculate(self, df):
        # -ts_distance_from_mean(midprice(bba_4_r, bun_to_bn_w, 15), 100)
        t = 200
        
        bba_4 = df['buy_smallorder_money'][-t:]
        sba_4 = df['sell_smallorder_money_v2'][-t:]
        bba_4_r = bba_4.sum(axis=1) / (bba_4.sum(axis=1) + sba_4.sum(axis=1))

        bun = df['BuyUniqueOrderNum'][-t:]
        bn = df['BuyTradeNum'][-t:]
        wt = df['weight'][-t:]
        bun_to_bn_w = (bun / bn * wt).sum(axis=1)

        factor = -ts_distance_from_mean(midprice(bba_4_r, bun_to_bn_w, 15), 100)
        factor = factor.values[-1]
        return factor
