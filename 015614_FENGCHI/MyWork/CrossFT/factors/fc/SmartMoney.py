# coding: utf-8
# Author：fengchi863
# Date ：2021/12/14 16:06

from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.crossUtils import *
from basic.operators import *


class SmartMoney(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 2
    author = 'fc'
    freq = '5mins'
    logic = '个股聪明钱因子，刻画每五分钟交易的聪明程度，分组求平均'
    article = '宽客学院 https://www.quantinfo.com/Article/View/735.html'
    basic_datas = {'daily': [], '30mins': [], '5mins': ['close_badj', 'volume'], '1min': []}

    def st_factor(self):
        close = self.database['5mins']['close_badj']
        vol = self.database['5mins']['volume']
        min_pct = dt_pct(close, 1)
        min_pct[:, :1, :] = np.nan
        ret = abs(min_pct) / vol ** 0.5
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
    # f = SmartMoney(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()
