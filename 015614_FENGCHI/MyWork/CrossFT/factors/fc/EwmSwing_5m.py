# coding: utf-8
# Author：fengchi863
# Date ：2021/12/17 13:59

from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.crossUtils import *
from basic.operators import *


class EwmSwing_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 2
    author = 'fc'
    freq = '5mins'
    logic = '该分钟前的一小时振幅的指数加权移动平均值，值越小，分钟波动越小，分组求平均'
    article = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': ['high', 'low', 'close'], '1min': []}

    def st_factor(self):
        high = self.database['5mins']['high']
        low = self.database['5mins']['low']
        close = self.database['5mins']['close']
        swing = (high - low) / dt_delay(close, 1)
        ret = dt_ewm(swing, 12)
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
    # f = EwmSwing_5m(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()