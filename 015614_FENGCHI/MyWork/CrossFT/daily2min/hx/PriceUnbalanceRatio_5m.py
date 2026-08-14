from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np


class PriceUnbalanceRatio_5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=10
    author='hx'
    logic='过去10日日内分时价格的不平衡度'
    article=''
    freq='5mins'
    basic_datas = {'5mins': ['close_badj', 'amt']}

    def st_factor(self):
        close = self.database['5mins']['close_badj']
        amt = self.database['5mins']['amt']
        pr1 = dt_mean(close, 48)
        pr2 = dt_mean(close * amt, 48) / dt_mean(amt, 48)
        factor = pr1 / pr2
        return factor

    def result(self):
        return self.cal_groupst()

if __name__=='__main__':
    val1 = cal_factor(start=20210101, end=20210630)
