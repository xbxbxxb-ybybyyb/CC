from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np


class TurnWeightMom20d_5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=21
    author='hx'
    logic='过去20日换手率加权动量'
    article=''
    freq='5mins'
    basic_datas = {'5mins': ['close_badj', 'turn_total']}

    def st_factor(self):
        close = self.database['5mins']['close_badj']
        turn = self.database['5mins']['turn_total']
        ret = dt_pct(close, 1)
        factor = dt_dwm2(ret, turn, 20)
        return factor

    def result(self):
        return self.cal_groupst()

if __name__=='__main__':
    val1 = cal_factor(start=20210101, end=20210630)

