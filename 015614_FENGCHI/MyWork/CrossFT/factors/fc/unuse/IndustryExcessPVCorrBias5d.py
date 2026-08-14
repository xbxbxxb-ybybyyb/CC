# coding: utf-8
# Author：fengchi863
# Date ：2021/11/15 11:27

from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.crossUtils import *
from basic.operators import *


class IndustryExcessPVCorrBias5d(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 10
    author = 'fc'
    freq = 'daily'
    logic = '量价相关性的行业超额，5日偏离度'
    article = ''
    basic_datas = {'daily': ['close_badj', 'a_mkt_cap', 'close_SZZZ'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        close = self.database['daily']['close_badj']
        cap = self.database['daily']['a_mkt_cap']
        szzz_close = self.database['daily']['close_SZZZ']
        szzz_close_pct = dt_pct(szzz_close, 1)
        stk_pct = dt_pct(close, 1)
        return stk_pct, cap, szzz_close_pct

    def calc_groupst(self):
        stk_pct, cap, szzz_close_pct = self.st_factor()
        group = sameshape(stk_pct, self.group_factor())
        a_mkt_weight = cap / st2groupst(cap, group, cross_sum)
        group_pct = st2groupst(a_mkt_weight * stk_pct, group, cross_sum)

        alpha = group_pct - np.repeat(szzz_close_pct, len(self.code_list), axis=2)
        alpha_std = dt_std(alpha, 5)
        ret = arr_match_index(alpha_std, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    # f = IndustryExcessPVCorrBias5d(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()