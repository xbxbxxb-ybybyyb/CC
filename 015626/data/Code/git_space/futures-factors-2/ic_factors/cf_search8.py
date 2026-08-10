from future_factor import FutureFactor
import numpy as np
import pandas as pd
import operators_all_wsc as op


class cf_search8(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight',
                          'BuyUniqueOrderNum',
                          'SellUniqueOrderNum',
                          'BuyTradeNum',
                          'SellTradeNum']
    normalize_size = 1200
    normalize_type = 'ts_rank'

    def calculate(self, df):
        # neg1(min2(midprice(bun_to_bn_w, bun_r, 15), ts_decay_linear(ts_max(bn_r, 15), 60)))

        wt = df['weight'][-75:]
        bun = df['BuyUniqueOrderNum'][-75:]
        sun = df['SellUniqueOrderNum'][-75:]
        bn = df['BuyTradeNum'][-75:]
        sn = df['SellTradeNum'][-75:]

        bun_s = bun.sum(axis=1)
        sun_s = sun.sum(axis=1)
        bun_r = bun_s / (bun_s + sun_s)

        bun_to_bn_w = ((bun / bn) * wt).sum(axis=1)

        bn_s = bn.sum(axis=1)
        sn_s = sn.sum(axis=1)
        bn_r = bn_s / (bn_s + sn_s)

        t1 = op.midprice(bun_to_bn_w, bun_r, 15)
        t2 = op.ts_decay_linear(op.ts_max(bn_r, 15), 60)

        factor = op.neg1(op.min2(t1, t2)).values[-1]
        return factor
