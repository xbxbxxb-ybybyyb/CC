# coding: utf-8
# Author：fengchi863
# Date ：2021/9/2 10:52
'''
个股收益率与行业收益率的均值的差异
'''
from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class IndMktRetCorr(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 20
    author = 'fc'
    freq = 'daily'
    logic = '10日行业个股收益差异性与市场的收益率的相关系数'
    article = 'A股“兴登堡凶兆“ 研究系列之一：市场面临较大调整压力'
    basic_datas = {'daily': ['close_badj', 'a_mkt_cap', 'close_SZZZ'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        close = self.database['daily']['close_badj']
        stk_ret = dt_pct(close, 1)
        szzz_close = self.database['daily']['close_SZZZ']
        szzz_ret = dt_pct(szzz_close.reshape(szzz_close.shape[0], 1, -1), 1)
        return stk_ret, szzz_ret

    def calc_groupst(self):
        stk_ret, szzz_ret = self.st_factor()
        self.group = sameshape(stk_ret, self.group_factor())
        stk_ret_diff = stk_ret - st2groupst(stk_ret, self.group, cross_mean)
        corr = dt_corr2(stk_ret_diff, np.repeat(szzz_ret, len(self.code_list), 2), 10)
        ret = arr_match_index(corr, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    # f = IndMktRetCorr()
    # print(f.result())
    cal_factor()
