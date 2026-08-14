# coding: utf-8
# Author：fengchi863
# Date ：2021/9/13 10:25


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class GroupNewLowPct(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 250
    author = 'fc'
    logic = '投资者情绪因子--纵向判断个股是否新低，然后横向统计组内新低比例（极值比例）'
    article = '行业轮动策略专题之（九）'
    freq = 'daily'
    basic_datas = {'daily': ['close_badj']}

    def st_factor(self):
        close_badj = self.database['daily']['close_badj']
        low = dt_max(close_badj, 250)
        ret = low == close_badj
        return ret

    def cal_groupst(self):
        ret = self.st_factor()
        stgroup = sameshape(ret, self.group_factor())
        low_num = st2groupst(ret, stgroup, cross_sum)

        group = np.ones_like(low_num)
        group_num = st2groupst(group, stgroup, cross_sum)
        ret = low_num / group_num
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    f = GroupNewLowPct()
    f.result()
    f.save_result()
