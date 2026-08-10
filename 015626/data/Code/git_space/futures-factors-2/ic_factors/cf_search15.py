import numpy as np
import pandas as pd
from future_factor import FutureFactor
from operators_wsc_for_srch import *


class cf_search15(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [
        'weight',
        'close',
        'amount',
        'BuyTradeMoney',
        'SellTradeMoney',
        'buy_smallorder_money',
        'sell_smallorder_money_v2'
    ]
    normalize_size = 1200
    normalize_type = 'ts_rank'

    def calculate(self, df):
        # -1 * mul2(df['bba_4_to_ba_w'], div2(cross_hub_num(df['ca_corr'], 95), df['sba_4_to_sa']))
        t = 200

        bba_4 = df['buy_smallorder_money'][-t:]
        ba = df['BuyTradeMoney'][-t:]
        wt = df['weight'][-t:]
        bba_4_to_ba_w = (bba_4 / ba * wt).sum(axis=1)

        close = df['close'][-t:]
        amount = df['amount'][-t:]
        ca_corr = close.corrwith(amount, axis=1)

        sba_4 = df['sell_smallorder_money_v2'][-t:]
        sa = df['SellTradeMoney'][-t:]
        sba_4_to_sa = sba_4.sum(axis=1) / sa.sum(axis=1)

        factor = -1 * mul2(bba_4_to_ba_w, div2(cross_hub_num(ca_corr, 95), sba_4_to_sa))
        factor = factor.values[-1]
        return factor