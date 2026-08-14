
from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


class xq_limitdown_num(crossFactor):
    cross_group='ones'
    cross_func='cross_sum'
    extend_days=40
    author='xq'
    logic='全市场跌停家数'
    article=None
    freq='daily'
    basic_datas = {'daily': ['limit_down']}

    def st_factor(self):
        return self.database['daily']['limit_down']


    def cal_groupst(self):
        limitdown = self.st_factor()
        self.group = sameshape(limitdown, self.group_factor())
        factor = st2groupst(limitdown, self.group, self.group_func())
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    f = xq_limitdown_num()
    f.save_result()