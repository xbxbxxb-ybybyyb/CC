# coding: utf-8
# Author：fengchi863
# Date ：2021/10/25 9:56

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class BigVolNetAmt(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 10
    author = 'fc'
    logic = '分钟买卖单金额比例，个股 * 分组'
    article = ''
    freq = '1min'
    basic_datas = {'1min': ['buytradeamt', 'selltradeamt']}

    def st_factor(self):
        buytradeamt = self.database['1min']['buytradeamt']
        selltradeamt = self.database['1min']['selltradeamt']

        stk_amt_ratio = div2(buytradeamt ,selltradeamt)

        return buytradeamt, selltradeamt, stk_amt_ratio

    def cal_groupst(self):
        buytradeamt, selltradeamt, stk_amt_ratio = self.st_factor()
        stgroup = sameshape(buytradeamt, self.group_factor())
        group_buy = st2groupst(buytradeamt, stgroup, cross_sum)
        group_sell = st2groupst(selltradeamt, stgroup, cross_sum)
        group_amt_ratio = group_buy / group_sell
        indicator = arr_match_index(stk_amt_ratio * group_amt_ratio, self.cal_date_range, self.date_range)
        return indicator

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    # f = BigVolNetAmt(start=20210401, end=20210501)
    # print(f.result())

    val = cal_factor('/data/user/015614/MyWork/CrossFT/factors/fc', 'BigVolNetAmt.py', {'1min': 10}, notrun=False)
