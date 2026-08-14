# coding: utf-8
# Author：fengchi863
# Date ：2021/8/18 14:20

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *

class CYBZMaArrange(crossFactor):
    cross_group = None
    cross_func = None
    extend_days = 60
    author = 'fc'
    factor_name = 'CYBZMaArrange'
    freq = 'daily'
    logic = '创业板指均线排列情况'
    article = '市场监控结论'
    basic_datas = {'daily': ['close_CYBZ']}

    def st_factor(self):
        close = self.database['daily']['close_CYBZ']
        ma5 = dt_mean(close,5)#.rolling(5).mean()
        ma10 = dt_mean(close,10)#close.rolling(10).mean()
        ma20 = dt_mean(close,20)#close.rolling(20).mean()
        ma60 = dt_mean(close,60)#close.rolling(60).mean()
        add1 = (ma5 > ma10)#.applymap(int)
        add2 = (ma10 > ma20)#.applymap(int)
        add3 = (ma20 > ma60)#.applymap(int)
        factor = add1 + add2 + add3
        factor = index2st(factor, len(self.code_list))#.values.reshape(-1, 1)
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        return self.st_factor()


if __name__ == '__main__':
    f = CYBZMaArrange()
    f.save_result()
