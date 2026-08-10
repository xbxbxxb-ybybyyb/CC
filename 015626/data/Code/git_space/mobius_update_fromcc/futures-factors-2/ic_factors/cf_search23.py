import numpy as np
import pandas as pd
from future_factor import FutureFactor
from operators_wsc_for_srch import *


class cf_search23(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [
        'weight',
        'sell_big_lo_amount',
        'sell_bigorder_money_v2',
        'SellTradeMoney',
        'sell_small_lo_amount',
        'sell_lo_amount',
    ]
    normalize_size = 1200
    normalize_type = 'ts_rank'

    def calculate(self, df):
        # add2(mul(ts_corr(df['bosa_2'], df['sba_2_to_sa_w'], 65), ts_min(df['bosa_4_to_osa'], 10)), ts_min(df['bosa_4_to_osa'], 10))
        t = 90

        wt = df['weight'][-t:]
        bosa_2 = df['sell_big_lo_amount'][-t:]
        sba_2 = df['sell_bigorder_money_v2'][-t:]
        sa = df['SellTradeMoney'][-t:]
        bosa_4 = df['sell_small_lo_amount'][-t:]
        osa = df['sell_lo_amount'][-t:]

        bosa_2 = bosa_2.sum(axis=1)
        sba_2_to_sa_w = (sba_2 / sa * wt).sum(axis=1)
        bosa_4_to_osa = bosa_4.sum(axis=1) / osa.sum(axis=1)

        factor = add2(mul2(ts_corr(bosa_2, sba_2_to_sa_w, 65), ts_min(bosa_4_to_osa, 10)), ts_min(bosa_4_to_osa, 10))
        factor = factor.values[-1]
        return factor
