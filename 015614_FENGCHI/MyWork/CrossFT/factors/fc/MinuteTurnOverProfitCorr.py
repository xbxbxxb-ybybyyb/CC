# coding: utf-8
# Author：fengchi863
# Date ：2021/9/1 11:14

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class MinuteTurnOverProfitCorr(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 0
    author = 'fc'
    freq = '1min'
    logic = '板块内个股开盘至今换手率与收益率的相关性'
    article = ''
    basic_datas = {'daily': ['a_mkt_cap', 'pre_close'], '30mins': [], '5mins': [], '1min': ['amt', 'close']}

    def st_factor(self):
        close = self.database['1min']['close']
        amt = self.database['1min']['amt']
        a_mkt_cap = self.database['daily']['a_mkt_cap']
        pre_close = self.database['daily']['pre_close']
        intra_pct = close / pre_close - 1
        turn_over = ts_cumsum(amt) / a_mkt_cap
        corr = ts_cumcorr2(turn_over, intra_pct)
        return corr

    def calc_groupst(self):
        ret = self.st_factor()
        self.group = sameshape(ret, self.group_factor())
        ret = st2groupst(ret, self.group, cross_mean)
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    f = MinuteTurnOverProfitCorr()
    print(f.result())
    f.save_result()
