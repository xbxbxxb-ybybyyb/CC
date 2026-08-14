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


class MktBigWithSmallRet(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 20
    author = 'fc'
    logic = '组内大市值减去组内小市值收益率/组内收益率的标准差'
    article = '技术指标系列报告之五'
    freq = 'daily'
    basic_datas = {'daily': ['close_badj']}

    def st_factor(self):
        close_badj = self.database['daily']['close_badj']
        pctchg = dt_pct(close_badj, 20)
        return pctchg

    def cal_groupst(self):
        pctchg = self.st_factor()
        stgroup = sameshape(pctchg, self.group_factor())
        groups = np.unique(stgroup[np.isfinite(stgroup)])
        rank = np.full(pctchg.shape, np.nan)
        for g in groups:
            val = stgroup == g
            rank = np.where(val, bottleneck.nanrankdata(np.where(val, -pctchg, np.nan), axis=2) /
                            np.repeat(val.sum(axis=2), len(self.code_list), axis=1)[:, None], rank)
        ret_st = st2groupst(pctchg, stgroup, cross_std)
        pctchg_copy = pctchg.copy()
        pctchg[rank > 0.1] = np.nan
        pctchg_copy[rank <= 0.1] = np.nan
        big_ret = st2groupst(pctchg, stgroup, cross_mean)
        small_ret = st2groupst(pctchg_copy, stgroup, cross_mean)
        ret = (big_ret - small_ret) / ret_st
        return ret

    def cal_customst(self):
        ret = self.cal_groupst()
        return arr_match_index(ret, self.cal_date_range, self.date_range)

    def result(self):
        return self.cal_customst()


if __name__ == '__main__':
    f = MktBigWithSmallRet()
    f.result()
    f.save_result()
