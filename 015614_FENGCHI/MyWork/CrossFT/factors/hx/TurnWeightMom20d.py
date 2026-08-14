from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np


class TurnWeightMom20d(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=21
    author='hx'
    logic='过去20日换手率加权动量'
    article=''
    freq='daily'
    basic_datas = {'daily': ['close_badj', 'turn']}

    def st_factor(self):
        close = self.database['daily']['close_badj']
        turn = self.database['daily']['turn']
        ret = dt_pct(close, 1)
        factor = dt_dwm2(ret, turn, 20)
        return factor

    def result(self):
        return self.cal_groupst()

if __name__=='__main__':
    val1 = cal_factor(numd={})
    val2 = cal_factor(numd={'daily': 10})
    gap = abs(val1 - val2)
    print(np.sum(np.where(np.isfinite(gap), gap, 0)))
