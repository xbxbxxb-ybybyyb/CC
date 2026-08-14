# coding: utf-8
# Author：fengchi863
# Date ：2021/12/23 17:57

from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.crossUtils import *
from basic.operators import *


class VolKurt(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 7
    author = 'fc'
    freq = 'daily'
    logic = '全天成交量峰度负取5日平均'
    article = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': ['volume']}

    def st_factor(self):
        vol = self.database['1min']['volume']
        EX = np.nanmean(vol, axis=1, keepdims=True)
        EX4 = np.nanmean((vol - EX) ** 4, axis=1)
        EX2 = np.nanmean((vol - EX) ** 2, axis=1) ** 2
        kurt = EX4 / EX2 - 3
        ret = dt_mean(kurt[:, None, :], 5)
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
    # f = VolKurt(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()
