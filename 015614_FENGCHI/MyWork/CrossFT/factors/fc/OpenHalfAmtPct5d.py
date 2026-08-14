# coding: utf-8
# Author：fengchi863
# Date ：2021/10/18 10:55

from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.crossUtils import *
from basic.operators import *


class OpenHalfAmtPct5d(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 10
    author = 'fc'
    logic = '开盘前半小时行业成交量占全市场成交量占比5日内行业均值/行业方差'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['close'], '1min': ['amt']}

    def st_factor(self):
        amt = self.database['1min']['amt']
        return amt

    def cal_groupst(self):
        amt = self.st_factor()
        close = self.database['daily']['close']
        stgroup = sameshape(close, self.group_factor())
        amt1000 = np.nansum(amt[:, :30, :], axis=1, keepdims=True)
        amt = np.nansum(amt, axis=1, keepdims=True)
        amt_pct = st2groupst(amt1000, stgroup,  self.group_func()) / \
                  st2groupst(amt, stgroup,  self.group_func())
        amt_pct = dt_mean(amt_pct, 5) / dt_std(amt_pct, 5)
        ret = arr_match_index(amt_pct, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    cal_factor()

