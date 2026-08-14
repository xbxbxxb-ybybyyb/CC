# coding: utf-8
# Author：fengchi863
# Date ：2021/9/16 10:04

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *

'''
行业内排序，然后取前5为True，再平铺到个股
基础数据：行业等权指数、沪深300指数
'''


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
                            np.repeat(val.sum(axis=2), factor.shape[2], axis=1)[:, None], rank)
    return rank


class IndAbnormal_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 20
    author = 'fc'
    logic = '组超额收益排序，取前五个组'
    article = '国金证券 20141108 – 行业异动专题分析报告'
    freq = '5mins'
    basic_datas = {'daily': ['fmarketval', 'close_badj'], '5mins': ['close_HS300', 'close_badj']}

    def st_factor(self):
        hs_300_index = self.database['5mins']['close_HS300']
        min_close = self.database['5mins']['close_badj']
        daily_close = self.database['daily']['close_badj']
        pctchg = min_close / np.repeat(daily_close, 48, axis=1)
        fmarketval = self.database['daily']['fmarketval']

        return hs_300_index, pctchg, fmarketval

    def cal_groupst(self):
        hs_300_index, pctchg, fmarketval = self.st_factor()
        self.group = sameshape(pctchg, self.group_factor())

        a_mkt_weight = fmarketval / st2groupst(fmarketval, self.group, cross_sum)
        industry_pctchg = st2groupst(a_mkt_weight * pctchg, self.group, cross_sum)

        alpha = industry_pctchg - hs_300_index

        rank = cross_rank(alpha, self.group, ascending=False)
        rank[rank <= 5] = 1
        rank[rank > 5] = 0

        return rank

    def cal_customst(self):
        ret = self.cal_groupst()
        return arr_match_index(ret, self.cal_date_range, self.date_range)

    def result(self):
        return self.cal_customst()


if __name__ == '__main__':
    # f = IndAbnormal_5m()
    # f.result()
    cal_factor()
