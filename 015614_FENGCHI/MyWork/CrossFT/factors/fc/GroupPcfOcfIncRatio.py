# coding: utf-8
# Author：fengchi863
# Date ：2021/9/13 10:25


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class GroupPcfOcfIncRatio(crossFactor):
    cross_group = 'sw2'
    cross_func = 'cross_mean'
    extend_days = 250
    author = 'fc'
    # logic = '组内个股经营现金流TTM增速 - 组内总经营现金流TTM增速'
    logic = '组内总经营现金流TTM增速'
    article = '基于股票因子映射的行业轮动方法'
    freq = 'daily'
    basic_datas = {'daily': ['pcf_ocf_ttm']}

    def st_factor(self):
        oper_rev_ttm = self.database['daily']['pcf_ocf_ttm']
        return oper_rev_ttm

    def cal_groupst(self):
        oper_rev_ttm = self.st_factor()
        stgroup = sameshape(oper_rev_ttm, self.group_factor())
        oper_rev_ttm_sum = st2groupst(oper_rev_ttm, stgroup,  self.group_func())
        group_inc = dt_pct(oper_rev_ttm_sum, 250)
        # stk_inc = dt_pct(oper_rev_ttm, 250)
        # ret = stk_inc - group_inc
        ret = group_inc
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    f = GroupPcfOcfIncRatio()
    f.result()
    f.save_result()
