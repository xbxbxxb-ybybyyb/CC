# coding: utf-8
# Author：fengchi863
# Date ：2021/12/30 15:52

from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.crossUtils import *
from basic.operators import *


class RetOrderActiveCorrPassive_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 2
    author = 'fc'
    freq = '5mins'
    logic = '主买成交的相对收益率与主卖成交的相对收益率的相关性，分组求平均'
    article = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': ['ret_order_active_buy', 'ret_order_active_sell'], '1min': []}

    def st_factor(self):
        ret_trade_buy = self.database['5mins']['ret_order_active_buy']
        ret_trade_sell = self.database['5mins']['ret_order_active_sell']
        ret = dt_corr2(ret_trade_buy, ret_trade_sell, 48)
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
    # f = TradeOrderActiveCorrPassive_5m(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()
