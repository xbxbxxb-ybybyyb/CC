
from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *
from basic.operators import *


class xq_boom_prem(crossFactor):
    cross_group='ones'
    cross_func='cross_mean'
    extend_days=40
    author='xq'
    logic='炸板溢价'
    article=None
    freq='daily'
    basic_datas = {'daily': ['close','limit_max','high','pct_chg']}

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        close = self.database['daily']['close']
        high = self.database['daily']['high']
        limit_max = self.database['daily']['limit_max']
        boom = dt_delay((high == limit_max) & (close != limit_max),1)
        pct = self.database['daily']['pct_chg']
        return boom, pct

    def cal_groupst(self):
        boom, pct = self.st_factor()
        boom_prem = np.where(boom == 1, pct, np.nan)
        self.group = sameshape(boom, self.group_factor())
        factor = st2groupst(boom_prem, self.group, self.group_func())
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    f = xq_boom_prem()
    f.save_result()