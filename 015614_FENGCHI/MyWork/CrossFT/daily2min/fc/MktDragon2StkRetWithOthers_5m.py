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


class MktDragon2StkRetWithOthers_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 20
    author = 'fc'
    logic = '组内龙头个股（按近10日涨跌幅靠前的前20%分位数）的日内平均收益率'
    article = ''
    freq = '5mins'
    basic_datas = {'daily': ['close_badj'], '5mins': ['close_badj']}

    def st_factor(self):
        min_close = self.database['5mins']['close_badj']
        daily_close = self.database['daily']['close_badj']
        min_pctchg = min_close / cross_resample(fill(daily_close[:-1,:,:], 1), self.freq)
        return min_pctchg

    def cal_groupst(self):
        pctchg = self.st_factor()
        stgroup = sameshape(pctchg, self.group_factor())
        groups = np.unique(stgroup[np.isfinite(stgroup)])
        shape = pctchg.shape
        rank = np.full(pctchg.shape, np.nan)
        for g in groups:
            val = stgroup == g
            rank = np.where(val, bottleneck.nanrankdata(np.where(val, -pctchg, np.nan), axis=2) /
                            np.repeat(val.sum(axis=2)[:,:,None], len(self.code_list), axis=2), rank)
        pctchg[rank > 0.2] = np.nan
        res = st2groupst(pctchg, stgroup, cross_mean)
        return res

    def cal_customst(self):
        # factor = self.st_factor() - self.cal_groupst()
        factor = self.cal_groupst()
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        return self.cal_customst()


if __name__ == '__main__':
    # f = MktDragon2StkRetWithOthers_5m(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()
