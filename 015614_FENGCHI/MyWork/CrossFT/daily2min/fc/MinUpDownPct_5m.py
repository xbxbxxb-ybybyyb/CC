# coding: utf-8
# Author：fengchi863
# Date ：2021/9/1 10:49

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class MinUpDownPct_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 5
    author = 'fc'
    freq = '5mins'
    logic = '板块内个股日内上涨分钟与下降分钟bar的数量的比值'
    article = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': ['close']}

    def st_factor(self):
        close = self.database['1min']['close']
        pct = dt_pct(close, 1)
        pct_up = np.where(pct > 0, 1, 0)
        pct_down = np.where(pct < 0, 1, 0)
        ret = ts_cumsum(pct_up) / ts_cumsum(pct_down)
        ret = cross_resample(ret, self.freq)
        return ret

    def calc_groupst(self):
        ret = self.st_factor()
        self.group = sameshape(ret, self.group_factor())
        ret = st2groupst(ret, self.group, cross_mean)
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    # f = MinUpDownPct_5m(start=20210401, end=20210501)
    # print(f.result())

    val = cal_factor()
