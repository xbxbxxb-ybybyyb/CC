import numpy as np
import pandas as pd
from future_factor import FutureFactor
from operators_wsc_for_srch import *


class wsc_hf_7_srch_ihbyif_if(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [
        'buy_superorder_count',
        'BuyUniqueOrderNum',
        'buy_smallorder_money',
        'sell_smallorder_money_v2',
        'buy_bigorder_count',
        'weight',
    ]
    normalize_size = 1200
    normalize_type = 'ts_rank'

    def calculate(self, df):
        # cross_hub_num(bbn_1_to_bun_w, 60) / bba_4_r * bbn_2_to_bun
        t = 120
        
        bbn_1 = df['buy_superorder_count'][-t:]
        bun = df['BuyUniqueOrderNum'][-t:]
        wt = df['weight'][-t:]
        bbn_1_to_bun_w = (bbn_1 / bun * wt).sum(axis=1)

        bba_4 = df['buy_smallorder_money'][-t:]
        sba_4 = df['sell_smallorder_money_v2'][-t:]
        bba_4_r = bba_4.sum(axis=1) / (bba_4.sum(axis=1) + sba_4.sum(axis=1))

        bbn_2 = df['buy_bigorder_count'][-t:]
        bbn_2_to_bun = bbn_2.sum(axis=1) / bun.sum(axis=1)
        
        factor = cross_hub_num(bbn_1_to_bun_w, 60) / bba_4_r * bbn_2_to_bun
        factor = factor.values[-1]
        return factor
