import numpy as np
import pandas as pd
from future_factor import FutureFactor
from operators_wsc_for_srch import *


class wsc_hf_11_srch_ihbyif_if(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [
        'SellTradeMoney',
        'SellUniqueOrderNum',
        'sell_bigorder_count_v2',
        'buy_smallorder_money',
        'sell_smallorder_money_v2',
        'BuyTradeNum',
        'SellTradeNum',
        'weight',
    ]
    normalize_size = 1200
    normalize_type = 'ts_rank'

    def calculate(self, df):
        # -(ts_skew(sa_to_sun_w, 60) + ts_skew(sbn_2_to_sun_w, 100) + bba_4_r_w + ts_skew(square(bn_r_w), 20) + ts_sum(bba_4_r, 10))
        t = 200
        
        sa = df['SellTradeMoney'][-t:]
        sun = df['SellUniqueOrderNum'][-t:]
        wt = df['weight'][-t:]
        sa_to_sun_w = (sa / sun * wt).sum(axis=1)

        sbn_2 = df['sell_bigorder_count_v2'][-t:]
        sbn_2_to_sun_w = (sbn_2 / sun * wt).sum(axis=1)

        bba_4 = df['buy_smallorder_money'][-t:]
        sba_4 = df['sell_smallorder_money_v2'][-t:]
        bba_4_r_w = (bba_4 / (bba_4 + sba_4) * wt).sum(axis=1)

        bn = df['BuyTradeNum'][-t:]
        sn = df['SellTradeNum'][-t:]
        bn_r_w = (bn / (bn + sn) * wt).sum(axis=1)

        bba_4_r = bba_4.sum(axis=1) / (bba_4.sum(axis=1) + sba_4.sum(axis=1))
        
        factor = -(ts_skew(sa_to_sun_w, 60) + ts_skew(sbn_2_to_sun_w, 100) + bba_4_r_w + ts_skew(square(bn_r_w), 20) + ts_sum(bba_4_r, 10))
        factor = factor.values[-1]
        return factor
