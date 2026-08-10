from future_factor import FutureFactor
import numpy as np
import pandas as pd
import operators_all_wsc as op


class cf_search6_IM(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight',
                          'BuyTradeNum',
                          'BuyUniqueOrderNum',
                          'SellUniqueOrderNum']
    normalize_size = 1200
    normalize_type = 'ts_rank'

    def calculate(self, df):
        # neg1(add2(midprice(bun_to_bn_w, bun_r, 15), bbands_up(bun_to_bn, 15)))

        wt = df['weight'][-15:]
        bn = df['BuyTradeNum'][-15:]
        bun = df['BuyUniqueOrderNum'][-15:]
        sun = df['SellUniqueOrderNum'][-15:]

        bun_s = bun.sum(axis=1)
        sun_s = sun.sum(axis=1)
        bun_r = bun_s / (bun_s + sun_s)

        bn_s = bn.sum(axis=1)
        bun_to_bn = bun_s / bn_s

        bun_to_bn_w = ((bun / bn) * wt).sum(axis=1)

        t1 = op.midprice(bun_to_bn_w, bun_r, 15)
        t2 = op.bbands_up(bun_to_bn, 15)

        factor = op.neg1(op.add2(t1, t2)).values[-1]
        return factor
