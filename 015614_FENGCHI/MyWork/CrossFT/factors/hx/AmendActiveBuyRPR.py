from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class AmendActiveBuyRPR(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=20
    author='hx'
    logic='收益率修正的主买成交额与过去10日均值之比 行业值与个股值之和'
    article='长江证券-基础因子研究（十八）：高频因子（十二），日内与日间-210606'
    freq='5mins'
    basic_datas = {'daily': [], '30mins': [], '5mins': ['ret_close', 'turn_total'], '1min': []}

    def st_factor(self):
        ret = np.clip(self.database['5mins']['ret_close'] / 1e3, -0.1, 0.1) * 10 + 1
        turn_total = np.clip(self.database['5mins']['turn_total'], 0, 10)
        turn_total *= ret
        turn_total[~ np.isfinite(turn_total)] = 0
        ar = ArrReshape()
        turn_total = ar.to2d(turn_total)
        wgt = np.ones(6) / 6
        turn_total = np.apply_along_axis(np.convolve, 0, turn_total, wgt, 'valid')
        turn_total = ar.to3d(fill(turn_total, 5))
        return turn_total

    def cal_groupst(self):
        fac = self.fac
        group = sameshape(fac, self.group_factor())
        res = st2groupst(fac, group, self.group_func())
        wgt = np.ones(10) / 10
        res /= fill(np.apply_along_axis(np.convolve, 0, res, wgt, 'valid'), 9)
        return res

    def cal_customst(self):
        self.fac = self.st_factor()
        fac = self.fac
        wgt = np.ones(10) / 10
        fac /= fill(np.apply_along_axis(np.convolve, 0, fac, wgt, 'valid'), 9)
        res = self.cal_groupst()
        return res + fac

    def result(self):
        return arr_match_index(self.cal_customst(), self.cal_date_range, self.date_range)

if __name__=='__main__':
    val1 = cal_factor()
