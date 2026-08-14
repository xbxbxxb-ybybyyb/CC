# coding: utf-8
# Author：fengchi863
# Date ：2021/8/18 14:20

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *


class MaArrange(crossFactor):
    cross_group = None
    cross_func = None
    extend_days = 60
    author = 'fc'
    freq = 'daily'
    logic = '均线排列情况'
    article = '市场监控结论'
    basic_datas = {'daily': ['close_badj']}

    def st_factor(self):
        close = self.database['daily']['close_badj']
        ma5 = dt_mean(close, 5)
        ma10 = dt_mean(close, 10)
        ma20 = dt_mean(close, 20)
        ma60 = dt_mean(close, 60)

        add1 = (ma5 > ma10).astype(int)
        add2 = (ma10 > ma20).astype(int)
        add3 = (ma20 > ma60).astype(int)
        factor = add1 + add2 + add3
        factor = arr_match_index(factor, self.cal_date_range, self.date_range)

        # add1 = (ma5 > ma10).applymap(int)
        # add2 = (ma10 > ma20).applymap(int)
        # add3 = (ma20 > ma60).applymap(int)
        # factor = add1 + add2 + add3
        # factor = df_match_index_col(factor, self.code_list, self.date_range)
        return factor

    def result(self):
        return self.st_factor()


if __name__ == '__main__':
    val1 = cal_factor(numd={})
    val2 = cal_factor(numd={'daily': 10})
    gap = abs(val1 - val2)
    print(np.nansum(gap))
    print(np.sum(np.where(np.isfinite(gap), gap, 0)))
