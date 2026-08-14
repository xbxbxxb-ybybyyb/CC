# coding: utf-8
# Author：fengchi863
# Date ：2021/9/3 14:20

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class ActiveBuySellDeltaRatio(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 0
    author = 'fc'
    freq = '5mins'
    logic = '板块内分钟主动买入与主动卖出成交金额的增加额对比'
    article = ''
    basic_datas = {'daily': [], '30mins': [],  '5mins': ['num_buy', 'num_sell', 'close']}

    def st_factor(self):
        num_buy = self.database['5mins']['num_buy']
        num_sell = self.database['5mins']['num_sell']
        close = self.database['5mins']['close']
        num_buy_delta = dt_delta(num_buy, 1)
        num_sell_delta = dt_delta(num_sell, 1)
        num_buy_amt_delta = num_buy_delta * close
        num_sell_amt_delta = num_sell_delta * close
        return num_buy_amt_delta, num_sell_amt_delta

    def calc_groupst(self):
        num_buy_amt_delta, num_sell_amt_delta = self.st_factor()
        self.group = sameshape(num_buy_amt_delta, self.group_factor())

        mean_buy = st2groupst(num_buy_amt_delta, self.group, cross_mean)
        mean_sell = st2groupst(num_sell_amt_delta, self.group, cross_mean)
        factor = arr_match_index(mean_buy / mean_sell, self.cal_date_range, self.date_range)
        return factor

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
  
    val2 = cal_factor()
   