# coding: utf-8
# Author：fengchi863
# Date ：2021/12/24 14:40

from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.crossUtils import *
from basic.operators import *


class AmtCloseCorr(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 10
    author = 'fc'
    freq = 'daily'
    logic = '全天分钟成交额与收盘价的相关系数，分组求均值'
    article = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': ['close_badj', 'amt']}

    def st_factor(self):
        amt = self.database['1min']['amt']
        close = self.database['1min']['close_badj']
        n = np.isfinite(close) | np.isfinite(amt)
        close[~ n] = 0
        amt[~ n] = 0
        cx = close.sum(axis=1)
        cy = amt.sum(axis=1)
        cx2 = (close ** 2).sum(axis=1)
        cy2 = (amt ** 2).sum(axis=1)
        cxy = (close * amt).sum(axis=1)
        cn = n.sum(axis=1)
        corr = (cxy - cx * cy / cn) / ((cx2 - cx ** 2 / cn) * (cy2 - cy ** 2 / cn)) ** 0.5
        corr[cn < 5] = np.nan
        corr = corr[:, None]
        return corr

    def calc_groupst(self):
        indicator = self.st_factor()
        group = sameshape(indicator, self.group_factor())
        group_ret = st2groupst(indicator, group, cross_mean)
        ret = arr_match_index(group_ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    # f = AmtCloseCorr(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()
