from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
from basic.crossOperators import *


class IndusStockMomDegree(crossFactor):
    cross_group='sw1'
    cross_func='cross_mad(平均绝对离差)'
    extend_days=10
    author='hx'
    logic='个股动量与行业内个股10日动量分化度之比'
    article=''
    freq='daily'
    basic_datas = {'daily': ['close_badj']}

    def st_factor(self):
        close = self.database['daily']['close_badj']
        ret = dt_pct(close, 10)
        return ret

    def cal_groupst(self):
        factor = self.st_factor()
        stgroup = sameshape(factor, self.group_factor())
        res = st2groupst(factor, stgroup,  self.group_func())
        factor -= res
        np.abs(factor, out=factor)
        res = st2groupst(factor, stgroup,  self.group_func()) * 1.483
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
