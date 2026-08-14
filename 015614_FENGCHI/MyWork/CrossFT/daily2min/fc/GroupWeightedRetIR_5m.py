# coding: utf-8
# Author：fengchi863
# Date ：2021/9/16 14:57

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *

'''
个股排序 + 行业排序
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


class GroupWeightedRetIR_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 5
    author = 'fc'
    logic = '组内流通市值加权涨跌幅个股排序+行业排序'
    article = ''
    freq = '5mins'
    basic_datas = {'daily': ['fmarketval', 'close_badj'], '5mins': ['close_badj']}

    def st_factor(self):
        min_close = self.database['5mins']['close_badj']
        daily_close = self.database['daily']['close_badj']
        fmarketval = self.database['daily']['fmarketval']
        pct_chg = min_close / np.repeat(daily_close, 48, axis=1)
        return pct_chg, fmarketval

    def cal_groupst(self):
        pctchg, fmarketval = self.st_factor()
        self.group = sameshape(pctchg, self.group_factor())
        a_mkt_weight = fmarketval / st2groupst(fmarketval, self.group, cross_sum)
        indicator = st2groupst(a_mkt_weight * pctchg, self.group, cross_sum)

        group = sameshape(indicator, self.group_factor())
        groups = np.unique(group[np.isfinite(group)])
        res = np.full(indicator.shape[:-1] + (len(groups),), np.nan)
        for j, g in enumerate(groups):
            res[..., j] = self.group_func()(np.where(group == g, indicator, np.nan), axis=-1)
        res = bottleneck.nanrankdata(res, axis=-1) / np.sum(np.isfinite(res), axis=-1, keepdims=True)
        res2 = np.full(indicator.shape, np.nan)
        for j, g in enumerate(groups):
            res2 = np.where(group == g, res[..., [j]], res2)
        return arr_match_index(res2, self.cal_date_range, self.date_range)

    def cal_customst(self):
        pctchg, fmarketval = self.st_factor()
        self.group = sameshape(pctchg, self.group_factor())
        a_mkt_weight = fmarketval / st2groupst(fmarketval, self.group, cross_sum)
        indicator = st2groupst(a_mkt_weight * pctchg, self.group, cross_sum)

        factor = bottleneck.nanrankdata(indicator, axis=-1) / np.sum(np.isfinite(indicator), axis=-1, keepdims=True)
        factor = arr_match_index(factor, self.cal_date_range, self.date_range)
        res = self.cal_groupst()
        return factor + res

    def result(self):
        return self.cal_customst()


if __name__ == '__main__':
    # f = GroupWeightedRetIR_5m(start=20210401, end=20210501)
    # f.result()

    cal_factor()
