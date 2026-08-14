# coding: utf-8
# Author：fengchi863
# Date ：2021/9/6 10:22

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *
import talib


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


class PVRankCorrSharpe5d(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 100
    author = 'fc'
    freq = 'daily'
    logic = '行业内量价秩的相关性，前5日夏普'
    article = ''
    basic_datas = {'daily': ['pct_chg', 'amt'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        pctchg = self.database['daily']['pct_chg']
        amt = self.database['daily']['amt']
        return pctchg, amt

    def calc_groupst(self):
        pctchg, amt = self.st_factor()
        self.group = sameshape(pctchg, self.group_factor())
        corr = dt_corr2(pctchg, amt, 50)
        sharpe = dt_sharpe(corr, 50)
        sharpe = st2groupst(sharpe, self.group, cross_mean)
        sharpe = arr_match_index(sharpe, self.cal_date_range, self.date_range)
        return sharpe

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    val1 = cal_factor(numd={})
    val2 = cal_factor(numd={'daily': 10})
    gap = abs(val1 - val2)
    print(np.sum(np.where(np.isfinite(gap), gap, 0)))
