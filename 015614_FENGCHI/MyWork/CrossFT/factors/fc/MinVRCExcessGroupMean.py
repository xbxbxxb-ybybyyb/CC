# coding: utf-8
# Author：fengchi863
# Date ：2021/11/10 14:56

from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.crossUtils import *
from basic.operators import *


class MinVRCExcessGroupMean(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 0
    author = 'fc'
    freq = '1min'
    logic = '日内时间加权筹码收益的标准差，筹码收益=收盘价相对于前期每一分钟的收益率，取平均'
    article = ''
    basic_datas = {'daily': ['close_badj'], '30mins': [], '5mins': [], '1min': ['close_badj', 'amt']}

    def st_factor(self):
        close = self.database['1min']['close_badj']
        amt = self.database['1min']['amt']
        daily_close = self.database['daily']['close_badj']
        daily_close = np.repeat(daily_close, 242, axis=1)
        pct = close / daily_close - 1
        ret = ts_cumstd(pct * amt)
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
    # f = MinVRCExcessGroupMean(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()
