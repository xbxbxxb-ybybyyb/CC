import numpy as np
import pandas as pd
from future_factor import FutureFactor
from operators_wsc_for_srch import *


class wsc_hf_17_srch_ihbyif_if(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [
        'buy_smallorder_money',
        'sell_smallorder_money_v2',
        'sell_bigorder_count_v2',
        'SellUniqueOrderNum',
        'buy_bigorder_money',
        'sell_bigorder_money_v2',
        'weight',
    ]
    normalize_size = 1200
    normalize_type = 'ts_rank'

    def calculate(self, df):
        # -midpoint(df['bba_4_r'], 10) * ts_sum(ts_skew(df['sbn_2_to_sun_w'], 100) + ts_skew(df['bba_2_r'], 20), 10)
        t = 200
        
        bba_4 = df['buy_smallorder_money'][-t:]
        sba_4 = df['sell_smallorder_money_v2'][-t:]
        bba_4_r = bba_4.sum(axis=1) / (bba_4.sum(axis=1) + sba_4.sum(axis=1))
        
        sbn_2 = df['sell_bigorder_count_v2'][-t:]
        sun = df['SellUniqueOrderNum'][-t:]
        wt = df['weight'][-t:]
        sbn_2_to_sun_w = (sbn_2 / sun * wt).sum(axis=1)
        
        bba_2 = df['buy_bigorder_money'][-t:]
        sba_2 = df['sell_bigorder_money_v2'][-t:]
        bba_2_r = bba_2.sum(axis=1) / (bba_2.sum(axis=1) + sba_2.sum(axis=1))
        
        factor = -midpoint(bba_4_r, 10) * ts_sum(ts_skew(sbn_2_to_sun_w, 100) + ts_skew(bba_2_r, 20), 10)
        factor = factor.values[-1]
        return factor
