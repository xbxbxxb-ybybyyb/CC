from future_factor import FutureFactor
import numpy as np
import pandas as pd
import operators_all_wsc as op


class cf_search5(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight',
                          'BuyTradeNum',
                          'BuyUniqueOrderNum',
                          'SellUniqueOrderNum',
                          'buy_bigorder_money',
                          'buy_bigorder_count']
    normalize_size = 1200
    normalize_type = 'ts_rank'

    def calculate(self, df):
        # neg1(min2(midprice(bun_to_bn_w, bun_r, 15), po(bba_to_bbn_w, 15, 90)))

        wt = df['weight'][-90:]
        bn = df['BuyTradeNum'][-90:]
        bun = df['BuyUniqueOrderNum'][-90:]
        sun = df['SellUniqueOrderNum'][-90:]
        bba = df['buy_bigorder_money'][-90:]
        bbn = df['buy_bigorder_count'][-90:]

        bun_to_bn_w = ((bun / bn) * wt).sum(axis=1)

        bba_to_bbn_w = ((bba / bbn) * wt).sum(axis=1)

        bun_s = bun.sum(axis=1)
        sun_s = sun.sum(axis=1)
        bun_r = bun_s / (bun_s + sun_s)

        t1 = op.midprice(bun_to_bn_w, bun_r, 15)
        t2 = op.po(bba_to_bbn_w, 15, 90)

        factor = op.neg1(op.min2(t1, t2)).values[-1]
        return factor
