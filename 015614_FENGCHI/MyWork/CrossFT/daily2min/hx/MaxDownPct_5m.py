from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np


class MaxDownPct_5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=10
    author='hx'
    logic='下影线长度占总K线长度之比'
    article=''
    freq='5mins'
    basic_datas = {'5mins': ['close_badj', 'open_badj', 'high_badj', 'low_badj']}

    def st_factor(self):
        close = self.database['5mins']['close_badj']
        opn = self.database['5mins']['open_badj']
        high = self.database['5mins']['high_badj']
        low = self.database['5mins']['low_badj']
        factor = dt_mean((np.fmin(opn, close) - low) / (high - low), 10)
        return factor

    def result(self):
        return self.cal_groupst()

if __name__=='__main__':
    val1 = cal_factor(start=20210101, end=20210630)
