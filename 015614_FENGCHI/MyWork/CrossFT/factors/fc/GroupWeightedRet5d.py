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


class GroupWeightedRet5d(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 5
    author = 'fc'
    logic = '组内流通市值加权涨跌幅5d排名取前5'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['close_badj', 'fmarketval']}

    def st_factor(self):
        close = self.database['daily']['close_badj']
        pctchg = dt_pct(close, 5)
        fmarketval = self.database['daily']['fmarketval']

        return pctchg, fmarketval

    def cal_groupst(self):
        pctchg, fmarketval = self.st_factor()
        self.group = sameshape(pctchg, self.group_factor())

        a_mkt_weight = fmarketval / st2groupst(fmarketval, self.group,  self.group_func())
        industry_pctchg = st2group(a_mkt_weight * pctchg, self.group,  self.group_func())
        industry_rank = np.argsort(np.argsort(-industry_pctchg))    # 从小到大排序
        ret = group2st(self.group, industry_rank)
        return ret

    def cal_customst(self):
        ret = self.cal_groupst()
        return arr_match_index(ret, self.cal_date_range, self.date_range)

    def result(self):
        return self.cal_customst()


if __name__ == '__main__':
    f = GroupWeightedRet5d()
    f.result()
    f.save_result()
