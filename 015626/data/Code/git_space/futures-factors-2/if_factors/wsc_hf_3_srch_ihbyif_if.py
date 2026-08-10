import numpy as np
import pandas as pd
from future_factor import FutureFactor
from operators_wsc_for_srch import *


class wsc_hf_3_srch_ihbyif_if(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [
        'buy_smallorder_money',
        'sell_smallorder_money_v2',
        'buy_bigorder_money',
        'sell_bigorder_money_v2',
        'buy_bigorder_count',
        'BuyUniqueOrderNum',
        'weight',
    ]
    normalize_size = 1200
    normalize_type = 'ts_rank'

    def calculate(self, df):
        # -(bba_4_r - bba_2_r_w + coefficient_of_variation(bbn_2_to_bun_w, 20))
        t = 40
        
        bba_4 = df['buy_smallorder_money'][-t:]
        sba_4 = df['sell_smallorder_money_v2'][-t:]
        bba_4_r = bba_4.sum(axis=1) / (bba_4.sum(axis=1) + sba_4.sum(axis=1))
        
        bba_2 = df['buy_bigorder_money'][-t:]
        sba_2 = df['sell_bigorder_money_v2'][-t:]
        wt = df['weight'][-t:]
        bba_2_r_w = ((bba_2 / (bba_2 + sba_2)) * wt).sum(axis=1)
        
        bbn_2 = df['buy_bigorder_count'][-t:]
        bun = df['BuyUniqueOrderNum'][-t:]
        bbn_2_to_bun_w = (bbn_2 / bun * wt).sum(axis=1)

        factor = -(bba_4_r - bba_2_r_w + coefficient_of_variation(bbn_2_to_bun_w, 20))
        factor = factor.values[-1]
        return factor
