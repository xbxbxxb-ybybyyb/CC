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


class HighPartTradeNumPct(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 10
    author = 'fc'
    logic = '日内高价区间内成交笔数占比 行业内均值'
    article = '东兴证券-另辟蹊径系列之一：基于高频快照数据的行为追踪因子-211015'
    freq = 'daily'
    basic_datas = {'1min': ['close_badj', 'tradenum']}

    def st_factor(self):
        close_badj = self.database['1min']['close_badj']
        tradenum = self.database['1min']['tradenum']
        
        perc = np.nanpercentile(close_badj, 50, axis=1, keepdims=True)
        flag = np.full_like(close_badj, fill_value=True)
        flag[close_badj > perc] = False

        trade_num_high = tradenum.copy()
        trade_num_high[flag.astype(bool)] = np.nan

        high_price_pct = np.nansum(trade_num_high, axis=1, keepdims=True) / \
                         np.nansum(tradenum, axis=1, keepdims=True)

        return high_price_pct

    def cal_groupst(self):
        indicator = self.st_factor()
        stgroup = sameshape(indicator, self.group_factor())
        indicator = st2groupst(indicator, stgroup, cross_sum)
        indicator = arr_match_index(indicator, self.cal_date_range, self.date_range)
        return indicator

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    # f = HighPartTradeNumPct(start=20210401, end=20210501)
    # print(f.result())

    val = cal_factor('/data/user/015614/MyWork/CrossFT/factors/fc', 'HighPartTradeNumPct.py', {'daily': 6}, notrun=False)

