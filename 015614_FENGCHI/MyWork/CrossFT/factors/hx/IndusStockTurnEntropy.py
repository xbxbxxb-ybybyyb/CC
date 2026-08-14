from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossOperators import *
from basic.crossFactor import crossFactor
import numpy as np


class IndusStockTurnEntropy(crossFactor):
    cross_group='sw1'
    cross_func='cross_plnp'
    extend_days=10
    author='hx'
    logic='个股10日换手率与行业内个股10日换手率信息熵之比'
    article=''
    freq='daily'
    basic_datas = {'daily': ['turn']}

    def st_factor(self):
        turn = self.database['daily']['turn']
        turn = dt_mean(turn, 10)
        return turn

    def cal_groupst(self):
        factor = self.st_factor()
        stgroup = sameshape(factor, self.group_factor())
        res = st2groupst(factor, stgroup, cross_sum)
        factor /= res
        factor *= np.log(factor)
        factor *= -1
        res = st2groupst(factor, stgroup, cross_sum)
        return arr_match_index(res, self.cal_date_range, self.date_range)

    def cal_customst(self):
        factor = self.st_factor()
        factor = arr_match_index(factor, self.cal_date_range, self.date_range)
        res = self.cal_groupst()
        return factor / res

    def result(self):
        return self.cal_customst()

if __name__=='__main__':
    val1 = cal_factor()
