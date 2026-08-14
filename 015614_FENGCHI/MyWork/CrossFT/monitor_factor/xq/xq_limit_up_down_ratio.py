from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


class xq_limit_up_down_ratio(crossFactor):
    cross_group='ones'
    cross_func='cross_sum'
    extend_days=40
    author='xq'
    logic='全市场涨跌停比值'
    article=None
    freq='daily'

    basic_datas = {'daily': ['limit_up','limit_down']}

    def st_factor(self):
        return self.database['daily']['limit_up'], self.database['daily']['limit_down']

    def cal_groupst(self):
        limitup, limitdown = self.st_factor()
        self.group = sameshape(limitup, self.group_factor())
        up_num = st2groupst(limitup, self.group, self.group_func())
        down_num = st2groupst(limitdown, self.group, self.group_func())
        factor = down_num/up_num
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    f = xq_limit_up_down_ratio()
    f.save_result()