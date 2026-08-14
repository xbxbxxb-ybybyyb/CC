# coding: utf-8
# Author：fengchi863
# Date ：2021/10/19 14:02

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
                            np.repeat(val.sum(axis=2), factor.shape[2], axis=1)[:, None], rank)
    return rank


class LowPartAmtPct(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 10
    author = 'fc'
    logic = '日内低价区间内成交量占全天成交量的比例 行业内均值'
    article = '东兴证券-另辟蹊径系列之一：基于高频快照数据的行为追踪因子-211015'
    freq = 'daily'
    basic_datas = {'1min': ['close_badj', 'amt']}

    def st_factor(self):
        close_badj = self.database['1min']['close_badj']
        amt = self.database['1min']['amt']

        perc = np.nanpercentile(close_badj, 50, axis=1, keepdims=True)
        flag = np.full_like(close_badj, fill_value=True)
        flag[close_badj < perc] = False

        amt_low = amt.copy()
        amt_low[flag.astype(bool)] = np.nan

        low_price_pct = np.nansum(amt_low, axis=1, keepdims=True) / \
                        np.nansum(amt, axis=1, keepdims=True)

        return low_price_pct

    def cal_groupst(self):
        indicator = self.st_factor()
        stgroup = sameshape(indicator, self.group_factor())
        indicator = st2groupst(indicator, stgroup, cross_sum)
        indicator = arr_match_index(indicator, self.cal_date_range, self.date_range)
        return indicator

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    # f = LowPartAmtPct(start=20210401, end=20210501)
    # print(f.result())

    val = cal_factor('/data/user/015614/MyWork/CrossFT/factors/fc', 'LowPartAmtPct.py', {'daily': 6}, notrun=False)
