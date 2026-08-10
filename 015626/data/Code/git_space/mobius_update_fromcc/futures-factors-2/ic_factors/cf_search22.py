import numpy as np
import pandas as pd
from future_factor import FutureFactor
from operators_wsc_for_srch import *


class cf_search22(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [
        'weight',
        'sell_bigorder_money_v2',
        'SellTradeMoney',
        'buy_small_lo_amount',
        'buy_lo_amount',
        'buy_superorder_money',
        'sell_superorder_money_v2',
    ]
    normalize_size = 1200
    normalize_type = 'ts_rank'

    def calculate(self, df):
        # -1 * min2(midprice(df['sba_2_to_sa_w'], df['boba_4_to_oba_w'], 30), ts_skew(df['bba_1_r_w'], 120))
        t = 150
        
        wt = df['weight'][-t:]
        sba_2 = df['sell_bigorder_money_v2'][-t:]
        sa = df['SellTradeMoney'][-t:]
        boba_4 = df['buy_small_lo_amount'][-t:]
        oba = df['buy_lo_amount'][-t:]
        bba_1 = df['buy_superorder_money'][-t:]
        sba_1 = df['sell_superorder_money_v2'][-t:]
        
        sba_2_to_sa_w = (sba_2 / sa * wt).sum(axis=1)
        boba_4_to_oba_w = (boba_4 / oba * wt).sum(axis=1)
        bba_1_r_w = (bba_1 / (bba_1 + sba_1) * wt).sum(axis=1)
        
        factor = -1 * min2(midprice(sba_2_to_sa_w, boba_4_to_oba_w, 30), ts_skew(bba_1_r_w, 120))
        factor = factor.values[-1]
        return factor
