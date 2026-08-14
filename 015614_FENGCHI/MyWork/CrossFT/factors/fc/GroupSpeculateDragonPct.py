# coding: utf-8
# Author：fengchi863
# Date ：2021/9/9 10:41

'''
板块内算排序，计算出前N
'''

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class GroupSpeculateDragonPct(crossFactor):
    cross_group = 'sw2'
    cross_func = 'cross_mean'
    extend_days = 2
    author = 'fc'
    logic = '组内投机龙头个股（按近2日涨跌幅靠前的前三名）的平均收益率'
    article = ''
    freq = '1min'
    basic_datas = {'daily': ['close_badj'], '1min': ['close_badj']}

    def st_factor(self):
        close_badj = self.database['daily']['close_badj']
        min_close = self.database['1min']['close_badj']
        close_badj = dt_delay(close_badj, 1)
        min_pctchg = min_close / np.repeat(close_badj, 242, 1) - 1
        return min_pctchg

    def cal_groupst(self):
        pctchg = self.st_factor()
        stgroup = sameshape(pctchg, self.group_factor())
        groups = np.unique(stgroup[np.isfinite(stgroup)])
        rank = np.full(pctchg.shape, np.nan)
        for g in groups:
            val = stgroup == g
            rank = np.where(val, bottleneck.nanrankdata(np.where(val, -pctchg, np.nan), axis=2), rank)
        pctchg[rank > 3] = np.nan
        res = st2groupst(pctchg, stgroup, cross_mean)
        return res

    def cal_customst(self):
        factor = self.cal_groupst()
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        return self.cal_customst()


if __name__ == '__main__':
    # f = MktDragon2StkRetWithOthers(start=20210401, end=20210501)
    # print(f.result())

    val = cal_factor()
