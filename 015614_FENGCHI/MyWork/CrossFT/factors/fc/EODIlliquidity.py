# coding: utf-8
# Author：fengchi863
# Date ：2021/9/2 13:33
'''
T-1日收益率除T-1日的成交额（市值加权）,分组内标准化
'''
from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class EODIlliquidity(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 20
    start = 20140701
    # start = 20210401
    end = 20210531
    author = 'fc'
    freq = 'daily'
    logic = 'T-1日收益率除T-1日的成交额（市值加权）标准化'
    article = ''
    basic_datas = {'daily': ['close_badj', 'a_mkt_cap', 'amt'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        close = self.database['daily']['close_badj']
        cap = self.database['daily']['a_mkt_cap']
        amt = self.database['daily']['amt']
        ret = dt_pct(close, 1)
        return ret, amt, cap

    def calc_groupst(self):
        ret, amt, cap = self.st_factor()
        self.group = sameshape(ret, self.group_factor())
        a_mkt_weight = cap / st2groupst(cap, self.group, cross_sum)
        ret = ret / (amt / a_mkt_weight)

        MEAN = st2groupst(ret, self.group, cross_mean)
        STD = st2groupst(ret, self.group, cross_std)
        ret = (ret - MEAN) / STD
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    f = EODIlliquidity()
    print(f.result())
    f.save_result()
