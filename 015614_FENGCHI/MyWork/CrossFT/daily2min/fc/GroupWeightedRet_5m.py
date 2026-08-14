# coding: utf-8
# Author：fengchi863
# Date ：2021/9/16 14:57

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


class GroupWeightedRet_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 5
    author = 'fc'
    logic = '组内流通市值加权涨跌幅1d当日排名取前5'
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
        industry_pctchg = st2group(a_mkt_weight * pctchg, self.group, cross_sum)
        industry_rank = np.argsort(np.argsort(-industry_pctchg))    # 从小到大排序
        ret = group2st(self.group, industry_rank)
        return ret

    def cal_customst(self):
        ret = self.cal_groupst()
        return arr_match_index(ret, self.cal_date_range, self.date_range)

    def result(self):
        return self.cal_customst()


if __name__ == '__main__':
    # f = GroupWeightedRet_5m(start=20210401, end=20210501)
    # f.result()

    cal_factor()
