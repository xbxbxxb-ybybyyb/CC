import numpy as np
import pandas as pd
from future_factor import FutureFactor
from operators_wsc_for_srch import *


class cf_search16(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [
        'weight',
        'BuyTradeMoney',
        'SellTradeMoney',
        'buy_smallorder_money',
        'sell_smallorder_money_v2',
        'BuyUniqueOrderNum',
        'BuyTradeNum'
    ]
    normalize_size = 1200
    normalize_type = 'ts_rank'

    def calculate(self, df):
        # -1 * div2(mul2(df['bba_4_to_ba_w'], div2(up_down_ratio(df['bun_to_bn'], 75, 120), df['sba_4_to_sa'])), df['ba_to_bun_w'])
        t = 240
        
        bba_4 = df['buy_smallorder_money'][-t:]
        ba = df['BuyTradeMoney'][-t:]
        wt = df['weight'][-t:]
        bba_4_to_ba_w = (bba_4 / ba * wt).sum(axis=1)
        
        bun = df['BuyUniqueOrderNum'][-t:]
        bn = df['BuyTradeNum'][-t:]
        bun_to_bn = bun.sum(axis=1) / bn.sum(axis=1)
    
        sba_4 = df['sell_smallorder_money_v2'][-t:]
        sa = df['SellTradeMoney'][-t:]
        sba_4_to_sa = sba_4.sum(axis=1) / sa.sum(axis=1)
        
        ba_to_bun_w = (ba / bun * wt).sum(axis=1)

        factor = -1 * div2(mul2(bba_4_to_ba_w, div2(up_down_ratio(bun_to_bn, 75, 120), sba_4_to_sa)), ba_to_bun_w)
        factor = factor.values[-1]
        return factor
