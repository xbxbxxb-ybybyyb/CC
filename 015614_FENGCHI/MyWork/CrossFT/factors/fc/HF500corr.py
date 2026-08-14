# coding: utf-8
# Author：fengchi863
# Date ：2021/8/30 14:09

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class HF500corr(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 25
    author = 'fc'
    freq = 'daily'
    logic = '个股涨跌幅与中证500指数的相关性'
    article = ''
    basic_datas = {'daily': ['pct_chg','close_SZZZ'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        pctchg = self.database['daily']['pct_chg']
        zz500_close = self.database['daily']['close_SZZZ']
        zz500_pctchg = dt_pct(zz500_close.reshape(len(self.cal_date_range), 1, -1), 1).reshape(len(self.cal_date_range), -1)
        return pctchg, zz500_pctchg

    def calc_groupst(self):
        pctchg, zz500_pctchg = self.st_factor()
        zz500_pctchg = np.repeat(zz500_pctchg.reshape(len(self.cal_date_range), 1, -1), len(self.code_list), axis=2)
        corr = dt_corr2(pctchg, zz500_pctchg, 20)

        self.group = sameshape(pctchg, self.group_factor())
        group_corr = st2groupst(corr, self.group, cross_mean)
        ret = arr_match_index(group_corr, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    val1 = cal_factor(numd={})
    val2 = cal_factor(numd={'daily': 10})
    gap = abs(val1 - val2)
    print(np.nansum(gap))
    print(np.sum(np.where(np.isfinite(gap), gap, 0)))
