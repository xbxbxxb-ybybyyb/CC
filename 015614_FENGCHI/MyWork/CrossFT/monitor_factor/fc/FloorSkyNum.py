# coding: utf-8
# Author：fengchi863
# Date ：2021/8/19 9:45

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *


class FloorSkyNum(crossFactor):
    cross_group = None
    cross_func = None
    extend_days = 0
    author = 'fc'
    freq = '1min'
    logic = '市场地天板的数量'
    article = '市场监控结论'
    basic_datas = {'daily': ['limit_max', 'limit_min'], '1min': ['close']}

    def st_factor(self):
        close = self.database['1min']['close']
        limit_max = self.database['daily']['limit_max']
        limit_min = self.database['daily']['limit_min']
        a = close == limit_max
        b = close == limit_min
        ab = a + ts_cummax(b)
        tmp = ts_cummax(ab) == 2
        return tmp

    def calc_factor(self):
        factor = self.st_factor()
        ret = np.repeat(np.nansum(factor, axis=2)[:, :, None], factor.shape[2], axis=2)
        return ret

    def result(self):
        return self.calc_factor()


if __name__ == '__main__':
    # f = FloorSkyNum(start=20210401, end=20210501)
    # print(f.result())
    cal_factor()
