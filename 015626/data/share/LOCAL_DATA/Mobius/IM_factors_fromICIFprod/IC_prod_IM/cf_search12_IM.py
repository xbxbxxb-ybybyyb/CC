from future_factor import FutureFactor
import numpy as np
import pandas as pd
import operators_all_wsc as op


class cf_search12_IM(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum',
                          'SellUniqueOrderNum',
                          'BuyTradeNum',
                          'SellTradeNum']
    normalize_size = 1200
    normalize_type = 'ts_rank'

    def calculate(self, df):
        # neg1(add2(midprice(bn_r, ts_ratio_from_mean(bun_r, 60), 15), bbands_up(bun_to_bn, 15)))

        bun = df['BuyUniqueOrderNum'][-75:]
        sun = df['SellUniqueOrderNum'][-75:]
        bn = df['BuyTradeNum'][-75:]
        sn = df['SellTradeNum'][-75:]

        bn_s = bn.sum(axis=1)
        sn_s = sn.sum(axis=1)
        bn_r = bn_s / (bn_s + sn_s)

        bun_s = bun.sum(axis=1)
        sun_s = sun.sum(axis=1)
        bun_r = bun_s / (bun_s + sun_s)

        bun_to_bn = bun_s / bn_s

        t1 = op.midprice(bn_r, op.ts_ratio_from_mean(bun_r, 60), 15)
        t2 = op.bbands_up(bun_to_bn, 15)

        factor = op.neg1(op.add2(t1, t2)).values[-1]
        return factor
