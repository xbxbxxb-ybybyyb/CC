import numpy as np
import pandas as pd
from future_factor import FutureFactor
from operators_wsc_for_srch import *


class wsc_hf_10_srch_ihbyif_if(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [
        'BuyUniqueOrderNum',
        'BuyTradeNum',
        'sell_smallorder_money_v2',
        'SellTradeMoney',
        'buy_smallorder_money',
        'weight',
    ]
    normalize_size = 1200
    normalize_type = 'ts_rank'

    def calculate(self, df):
        # -(bun_to_bn_w + bbands_down(ts_rank(sba_4_to_sa_w, 75), 60) + ts_sum(bba_4_r, 10))
        t = 150
        
        bun = df['BuyUniqueOrderNum'][-t:]
        bn = df['BuyTradeNum'][-t:]
        wt = df['weight'][-t:]
        bun_to_bn_w = (bun / bn * wt).sum(axis=1)

        sba_4 = df['sell_smallorder_money_v2'][-t:]
        sa = df['SellTradeMoney'][-t:]
        sba_4_to_sa_w = (sba_4 / sa * wt).sum(axis=1)

        bba_4 = df['buy_smallorder_money'][-t:]
        bba_4_r = bba_4.sum(axis=1) / (bba_4.sum(axis=1) + sba_4.sum(axis=1))
        
        factor = -(bun_to_bn_w + bbands_down(ts_rank(sba_4_to_sa_w, 75), 60) + ts_sum(bba_4_r, 10))
        factor = factor.values[-1]
        return factor
