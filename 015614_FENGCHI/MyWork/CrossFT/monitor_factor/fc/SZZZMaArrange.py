# coding: utf-8
# Author：fengchi863
# Date ：2021/8/18 14:20

from basic.crossFactor import crossFactor
from basic.crossUtils import *


class SZZZMaArrange(crossFactor):
    cross_group = None
    cross_func = None
    extend_days = 60
    author = 'fc'
    factor_name = 'SZZZMaArrange'
    freq = 'daily'
    logic = '上证综指均线排列情况'
    article = '市场监控结论'
    basic_datas = {'daily': ['close_SZZZ']}

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        close = self.database['daily']['close_SZZZ']
        ma5 = dt_mean(close, 5)
        ma10 = dt_mean(close, 10)
        ma20 = dt_mean(close, 20)
        ma60 = dt_mean(close, 60)
        add1 = (ma5 > ma10)
        add2 = (ma10 > ma20)
        add3 = (ma20 > ma60)
        factor = add1 + add2 + add3
        factor = index2st(factor, len(self.code_list))
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        return self.st_factor()


if __name__ == '__main__':
    cal_factor()
