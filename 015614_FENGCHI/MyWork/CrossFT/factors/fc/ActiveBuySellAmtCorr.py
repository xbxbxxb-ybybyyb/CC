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


class ActiveBuySellAmtCorr(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 5
    author = 'fc'
    logic = '全天主买主卖最强时段与价格的相关性对比 个股值 * 行业均值'
    article = ''
    freq = 'daily'
    basic_datas = {'1min': ['activesellorderamt', 'activebuyorderamt', 'close_badj']}

    def st_factor(self):
        activebuyorderamt = self.database['1min']['activebuyorderamt']
        close_badj = self.database['1min']['close_badj']

        MEAN = np.nanmean(activebuyorderamt, axis=1, keepdims=True)
        STD = np.nanstd(activebuyorderamt, axis=1, keepdims=True)
        active_flag = activebuyorderamt < np.repeat((MEAN + STD), 242, axis=1)
        activebuyorderamt[active_flag] = np.nan
        close_badj[active_flag] = np.nan

        EX = np.nanmean(activebuyorderamt, axis=1)
        EY = np.nanmean(close_badj, axis=1)
        EXY = np.nanmean(activebuyorderamt * close_badj, axis=1)
        STDX = np.nanstd(activebuyorderamt, axis=1)
        STDY = np.nanstd(close_badj, axis=1)
        corr1 = (EXY - EX * EY) / (STDX * STDY)

        activesellorderamt = self.database['1min']['activesellorderamt']
        close_badj = self.database['1min']['close_badj']

        MEAN = np.nanmean(activesellorderamt, axis=1, keepdims=True)
        STD = np.nanstd(activesellorderamt, axis=1, keepdims=True)
        active_flag = activesellorderamt < np.repeat((MEAN + STD), 242, axis=1)
        activesellorderamt[active_flag] = np.nan
        close_badj[active_flag] = np.nan

        EX = np.nanmean(activesellorderamt, axis=1)
        EY = np.nanmean(close_badj, axis=1)
        EXY = np.nanmean(activesellorderamt * close_badj, axis=1)
        STDX = np.nanstd(activesellorderamt, axis=1)
        STDY = np.nanstd(close_badj, axis=1)
        corr2 = (EXY - EX * EY) / (STDX * STDY)
        return corr1 / corr2

    def cal_groupst(self):
        indicator = self.st_factor()
        stgroup = sameshape(indicator, self.group_factor())
        ret = st2groupst(indicator, stgroup, cross_mean)
        ret = arr_match_index(ret[:, None, :], self.cal_date_range, self.date_range)
        indicator = arr_match_index(indicator[:, None, :], self.cal_date_range, self.date_range)
        return indicator * ret

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    # f = ActiveBuySellAmtCorr(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()

