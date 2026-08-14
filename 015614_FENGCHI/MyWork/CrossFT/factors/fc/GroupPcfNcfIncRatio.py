# coding: utf-8
# Author：fengchi863
# Date ：2021/9/13 10:25


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class GroupPcfNcfIncRatio(crossFactor):
    cross_group = 'sw2'
    cross_func = 'cross_mean'
    extend_days = 250
    author = 'fc'
    # logic = '组内个股现金净流量增速 - 组内总现金净流量LYR增速'
    logic = '组内总现金净流量LYR增速'
    article = '基于股票因子映射的行业轮动方法'
    freq = 'daily'
    basic_datas = {'daily': ['pcf_ncf_ttm']}

    def st_factor(self):
        oper_rev_ttm = self.database['daily']['pcf_ncf_ttm']
        return oper_rev_ttm

    def cal_groupst(self):
        oper_rev_ttm = self.st_factor()
        stgroup = sameshape(oper_rev_ttm, self.group_factor())
        oper_rev_ttm_sum = st2groupst(oper_rev_ttm, stgroup, cross_sum)
        group_inc = dt_pct(oper_rev_ttm_sum, 250)
        # stk_inc = dt_pct(oper_rev_ttm, 250)
        # ret = stk_inc - group_inc
        ret = group_inc
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    f = GroupPcfNcfIncRatio()
    f.result()
    f.save_result()
