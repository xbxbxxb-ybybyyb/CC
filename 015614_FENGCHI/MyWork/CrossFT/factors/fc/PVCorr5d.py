# coding: utf-8
# Author：fengchi863
# Date ：2021/12/23 19:16

from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.crossUtils import *
from basic.operators import *


class PVCorr5d(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 2
    author = 'fc'
    freq = 'daily'
    logic = '全天量价相关性，先取负值，求5日均值，分组求平均'
    article = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': ['close_badj', 'volume']}

    def st_factor(self):
        close = self.database['1min']['close_badj']
        vol = self.database['1min']['volume']
        n = np.isfinite(close) | np.isfinite(vol)
        close[~ n] = 0
        vol[~ n] = 0
        cx = close.sum(axis=1)
        cy = vol.sum(axis=1)
        cx2 = (close ** 2).sum(axis=1)
        cy2 = (vol ** 2).sum(axis=1)
        cxy = (close * vol).sum(axis=1)
        cn = n.sum(axis=1)
        corr = (cxy - cx * cy / cn) / ((cx2 - cx ** 2 / cn) * (cy2 - cy ** 2 / cn)) ** 0.5
        corr[cn < 5] = np.nan
        corr = corr[:, None]
        ret = dt_mean(-corr, 5)
        return ret

    def calc_groupst(self):
        indicator = self.st_factor()
        group = sameshape(indicator, self.group_factor())
        group_ret = st2groupst(indicator, group, cross_mean)
        ret = arr_match_index(group_ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    # f = PVCorr5d(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()
