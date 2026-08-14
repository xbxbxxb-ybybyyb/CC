# coding: utf-8
# Author：fengchi863
# Date ：2021/9/23 10:41

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class IntraMaxDrawdownWithOpenMean(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_median'
    extend_days = 0
    author = 'fc'
    freq = '1min'
    logic = '板块内相对开盘价的最大跌幅的中位数'
    article = ''
    basic_datas = {'daily': ['open_badj'], '30mins': [], '5mins': [], '1min': ['close_badj']}

    def st_factor(self):
        daily_open = self.database['daily']['open_badj']
        close = self.database['1min']['close_badj']
        pctchg = close / np.repeat(daily_open, 242, axis=1) - 1
        max_drawdown = ts_cummin(pctchg)
        return max_drawdown

    def calc_groupst(self):
        max_drawdown = self.st_factor()
        self.group = sameshape(max_drawdown, self.group_factor())
        ret = st2groupst(max_drawdown, self.group, self.group_func())
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    f = IntraMaxDrawdownWithOpenMean()
    print(f.result())
    f.save_result()
