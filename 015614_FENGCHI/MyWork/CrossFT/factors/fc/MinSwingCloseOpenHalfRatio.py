# coding: utf-8
# Author：fengchi863
# Date ：2021/11/9 14:51

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class MinSwingCloseOpenHalfRatio(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 5
    author = 'fc'
    freq = 'daily'
    logic = '当日最后半小时的平均振幅相对上个交易日前半个小时的振幅之比'
    article = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': ['high_badj', 'low_badj']}

    def st_factor(self):
        high = self.database['1min']['high_badj']
        low = self.database['1min']['low_badj']
        swing = (high - low) / low
        last_day_swing = fill(swing[:-1, :, :], 1, axis=0)
        ret = np.nanmean(swing[:, -30:, :], axis=1) / np.nanmean(last_day_swing[:, -30:, :], axis=1)
        return ret

    def calc_groupst(self):
        ret = self.st_factor()
        group = sameshape(ret, self.group_factor())
        ret = st2groupst(ret, group, cross_mean)
        factor = arr_match_index(ret, self.cal_date_range, self.date_range)
        return factor

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    # f = MinSwingCloseOpenHalfRatio(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()