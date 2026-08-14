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


class GroupDragon2TurnMedian(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 5
    author = 'fc'
    logic = '组内龙头个股（按近10日涨跌幅靠前的前20%分位数）的5日换手率中位值'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['turn', 'close_badj']}

    def st_factor(self):
        close_badj = self.database['daily']['close_badj']
        pctchg = dt_pct(close_badj, 5)
        turn = self.database['daily']['turn']
        return turn, pctchg

    def cal_groupst(self):
        turn, pctchg = self.st_factor()
        stgroup = sameshape(pctchg, self.group_factor())
        groups = np.unique(stgroup[np.isfinite(stgroup)])
        shape = pctchg.shape
        rank = np.full(pctchg.shape, np.nan)
        for g in groups:
            val = stgroup == g
            rank = np.where(val, bottleneck.nanrankdata(np.where(val, -pctchg, np.nan), axis=2) /
                            np.repeat(val.sum(axis=2), len(self.code_list), axis=1)[:, None], rank)
        turn[rank > 0.2] = np.nan
        res = st2groupst(turn, stgroup,  self.group_func())
        return res

    def cal_customst(self):
        # factor = self.st_factor() - self.cal_groupst()
        factor = self.cal_groupst()
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        return self.cal_customst()


if __name__ == '__main__':
    f = GroupDragon2TurnMedian()
    f.result()
    f.save_result()
