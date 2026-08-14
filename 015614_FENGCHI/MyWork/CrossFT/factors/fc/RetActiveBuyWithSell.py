# coding: utf-8
# Author：fengchi863
# Date ：2021/9/3 10:18

'''
盘口数据组内变化率
'''

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class RetActiveBuyWithSell(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 0
    author = 'fc'
    freq = '1min'
    logic = '行业内个股主买主卖收益率对比'
    article = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': ['ret_order_active_buy', 'ret_order_active_sell']}

    def st_factor(self):
        ret_order_active_buy = self.database['1min']['ret_order_active_buy']
        ret_order_active_sell = self.database['1min']['ret_order_active_sell']
        return ret_order_active_buy, ret_order_active_sell

    def calc_groupst(self):
        ret_order_active_buy, ret_order_active_sell = self.st_factor()
        self.group = sameshape(ret_order_active_buy, self.group_factor())

        mean_buy = st2groupst(ret_order_active_buy, self.group, cross_mean)
        mean_sell = st2groupst(ret_order_active_sell, self.group, cross_mean)
        factor = arr_match_index(mean_buy / mean_sell, self.cal_date_range, self.date_range)
        return factor

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    f = RetActiveBuyWithSell()
    print(f.result())
    f.save_result()
