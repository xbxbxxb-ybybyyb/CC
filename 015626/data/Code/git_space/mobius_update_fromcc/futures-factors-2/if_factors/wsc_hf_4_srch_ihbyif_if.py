import numpy as np
import pandas as pd
from future_factor import FutureFactor
from operators_wsc_for_srch import *


class wsc_hf_4_srch_ihbyif_if(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [
        'buy_smallorder_money',
        'sell_smallorder_money_v2',
        'BuyUniqueOrderNum',
        'SellUniqueOrderNum',
        'buy_bigorder_money',
        'BuyTradeMoney',
        'weight',
    ]
    normalize_size = 1200
    normalize_type = 'ts_rank'

    def calculate(self, df):
        # -bba_4_r * (midpoint(bun_r, 15) + ppo(bba_2_to_ba_w, 20, 90))
        t = 180
        
        bba_4 = df['buy_smallorder_money'][-t:]
        sba_4 = df['sell_smallorder_money_v2'][-t:]
        bba_4_r = bba_4.sum(axis=1) / (bba_4.sum(axis=1) + sba_4.sum(axis=1))
        
        bun = df['BuyUniqueOrderNum'][-t:]
        sun = sun = df['SellUniqueOrderNum'][-t:]
        bun_r = bun.sum(axis=1) / (bun.sum(axis=1) + sun.sum(axis=1))
        
        bba_2 = df['buy_bigorder_money'][-t:]
        ba = df['BuyTradeMoney'][-t:]
        wt = df['weight'][-t:]
        bba_2_to_ba_w = (bba_2 / ba * wt).sum(axis=1)

        factor = -bba_4_r * (midpoint(bun_r, 15) + ppo(bba_2_to_ba_w, 20, 90))
        factor = factor.values[-1]
        return factor
