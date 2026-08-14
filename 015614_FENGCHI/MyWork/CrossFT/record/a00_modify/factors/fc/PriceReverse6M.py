# coding: utf-8
# Author：fengchi863
# Date ：2021/8/23 10:23
'''
反转类因子
'''

from basic.crossFactor import crossFactor
from basic.crossUtils import *


class PriceReverse6M(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=130
    author='fc'
    freq='daily'
    logic='6个月股价反转'
    article='广发证券-20170330-多因子Alpha系列报告之三十'


    def st_factor(self):
        N = 120
        ret = get_daily_1factor('close_badj', self.cal_date_range, self.code_list)
        pctchg = ret.pct_change(N)
        ret = df_match_index_col(pctchg, self.code_list, self.cal_date_range)
        return ret

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    f = PriceReverse6M()
    f.save_result()