from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


class xq_down_ratio(crossFactor):
    cross_group='ones'
    cross_func='cross_mean'
    extend_days=40
    author='xq'
    logic='全市场下跌家数占比'
    article=None
    freq='daily'

    basic_datas = {'daily': ['pct_chg']}

    def st_factor(self):
        return self.database['daily']['pct_chg']

    def cal_groupst(self):
        pct = self.st_factor()
        self.group = sameshape(pct, self.group_factor())
        factor = st2groupst((pct<0), self.group, self.group_func())
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    f = xq_down_ratio()
    f.save_result()