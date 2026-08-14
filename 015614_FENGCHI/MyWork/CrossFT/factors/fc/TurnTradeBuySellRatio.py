# coding: utf-8
# Author：fengchi863
# Date ：2021/9/3 14:37

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class TurnTradeBuySellRatio(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 0
    author = 'fc'
    freq = '1min'
    logic = '板块主动买卖单换手累计均值之比'
    article = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': ['turn_trade_buy', 'turn_trade_sell']}

    def st_factor(self):
        turn_trade_buy = self.database['1min']['turn_trade_buy']
        turn_trade_sell = self.database['1min']['turn_trade_sell']
        return turn_trade_buy, turn_trade_sell

    def calc_groupst(self):
        turn_trade_buy, turn_trade_sell = self.st_factor()
        self.group = sameshape(turn_trade_buy, self.group_factor())
        buy_cumsum = ts_cumsum(turn_trade_buy)
        sell_cumsum = ts_cumsum(turn_trade_sell)
        mean_buy = st2groupst(buy_cumsum, self.group, cross_mean)
        mean_sell = st2groupst(sell_cumsum, self.group, cross_mean)
        factor = arr_match_index(mean_buy / mean_sell, self.cal_date_range, self.date_range)
        return factor

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    f = TurnTradeBuySellRatio()
    print(f.result())
    f.save_result()
