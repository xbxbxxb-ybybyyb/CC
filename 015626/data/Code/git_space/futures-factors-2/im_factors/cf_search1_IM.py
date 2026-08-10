from future_factor import FutureFactor
import numpy as np
import pandas as pd
import operators_all_wsc as op


class cf_search1_IM(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeNum',
                          'BuyUniqueOrderNum',
                          'SellUniqueOrderNum']
    normalize_size = 1200
    normalize_type = 'ts_rank'

    def calculate(self, df):
        # neg1(min2(ts_max(bun_r, 15), dema(bun_to_bn, 45)))

        bn = df['BuyTradeNum'][-45:]
        bun = df['BuyUniqueOrderNum'][-45:]
        sun = df['SellUniqueOrderNum'][-45:]

        bun_s = bun.sum(axis=1)
        sun_s = sun.sum(axis=1)
        bun_r = bun_s / (bun_s + sun_s)

        bn_s = bn.sum(axis=1)
        bun_to_bn = bun_s / bn_s

        t1 = op.ts_max(bun_r, 15)
        t2 = op.dema(bun_to_bn, 45)

        factor = op.neg1(op.min2(t1, t2)).values[-1]
        return factor
