import numpy as np
import pandas as pd
from future_factor import FutureFactor
from operators_wsc_for_srch import *


class cf_search3_if(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [
        'sell_superorder_count_v2',
        'SellUniqueOrderNum',
        'BuyUniqueOrderNum',
        'BuyTradeNum',
        'weight',
    ]
    normalize_size = 1200
    normalize_type = 'ts_rank'

    def calculate(self, df):
        # -midprice(add2(ppo(sbn_1_to_sun_w, 80, 115), bun_to_bn_w), bun_r, 15)
        t = 230
        
        sbn_1 = df['sell_superorder_count_v2'][-t:]
        sun = sun = df['SellUniqueOrderNum'][-t:]
        wt = df['weight'][-t:]
        sbn_1_to_sun_w = (sbn_1 / sun * wt).sum(axis=1)

        bun = df['BuyUniqueOrderNum'][-t:]
        bn = df['BuyTradeNum'][-t:]
        bun_to_bn_w = (bun / bn * wt).sum(axis=1)

        bun_r = bun.sum(axis=1) / (bun.sum(axis=1) + sun.sum(axis=1))

        factor = -midprice(add2(ppo(sbn_1_to_sun_w, 80, 115), bun_to_bn_w), bun_r, 15)
        factor = factor.values[-1]
        return factor
