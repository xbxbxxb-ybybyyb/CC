# coding: utf-8
# Author：fengchi863
# Date ：2021/9/13 10:25


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class GroupPsTtmIncRatio(crossFactor):
    cross_group = 'sw2'
    cross_func = 'cross_mean'
    extend_days = 250
    author = 'fc'
    # logic = '组内个股市销率TTM增速 - 组内平均市销率TTM增速'
    logic = '组内平均市销率TTM增速'
    article = '基于股票因子映射的行业轮动方法'
    freq = 'daily'
    basic_datas = {'daily': ['ps_ttm']}

    def st_factor(self):
        ps_ttm = self.database['daily']['ps_ttm']
        return ps_ttm

    def cal_groupst(self):
        ps_ttm = self.st_factor()
        stgroup = sameshape(ps_ttm, self.group_factor())
        ps_ttm_mean = st2groupst(ps_ttm, stgroup, cross_mean)
        group_inc = dt_pct(ps_ttm_mean, 250)
        # stk_inc = dt_pct(ps_ttm, 250)
        # ret = stk_inc - group_inc
        ret = group_inc
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    f = GroupPsTtmIncRatio()
    f.result()
    f.save_result()
