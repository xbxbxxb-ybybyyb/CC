# coding: utf-8
# Author：fengchi863
# Date ：2021/10/18 11:07

import bottleneck
import numpy as np

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


def cross_rank(factor, group, ascending=True, pct=False):
    if ~ascending:
        factor = -factor
    groups = np.unique(group[np.isfinite(group)])
    rank = np.full(factor.shape, np.nan)
    if ~pct:
        for g in groups:
            val = group == g
            rank = np.where(val, bottleneck.nanrankdata(np.where(val, factor, np.nan), axis=2), rank)

    if pct:
        for g in groups:
            val = group == g
            rank = np.where(val, bottleneck.nanrankdata(np.where(val, factor, np.nan), axis=2) /
                            np.repeat(val.sum(axis=2)[:, :, None], factor.shape[2], axis=2), rank)
    return rank


class LargeMktStkIndAlphaMean5d_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 5
    author = 'fc'
    logic = '组内市值从大到小前30%个股的半小时行业超额均值'
    article = ''
    freq = '5mins'
    basic_datas = {'daily': ['a_mkt_cap'], '5mins': ['close_badj']}

    def st_factor(self):
        close = self.database['5mins']['close_badj']
        stk_pctchg = dt_pct(close, 6)
        return stk_pctchg

    def cal_groupst(self):
        stk_pctchg = self.st_factor()
        a_mkt_cap = self.database['daily']['a_mkt_cap']
        a_mkt_cap = cross_resample(a_mkt_cap, self.freq)
        stgroup = sameshape(stk_pctchg, self.group_factor())
        a_mkt_weight = a_mkt_cap / st2groupst(a_mkt_cap, stgroup, cross_sum)
        indicator = st2groupst(a_mkt_weight * stk_pctchg, stgroup, cross_sum)

        stk_alpha = stk_pctchg - indicator

        rank = cross_rank(a_mkt_cap, stgroup, ascending=False, pct=True)
        stk_alpha[rank > 0.3] = np.nan
        res = st2groupst(stk_alpha, stgroup, cross_mean)
        return res

    def cal_customst(self):
        factor = self.cal_groupst()
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        return self.cal_customst()


if __name__ == '__main__':
    # f = LargeMktStkIndAlphaMean5d_5m(start=20210401, end=20210501)
    # print(f.result())

    val = cal_factor()

