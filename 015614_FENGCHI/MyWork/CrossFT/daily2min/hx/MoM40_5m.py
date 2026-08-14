from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np


class MoM40_5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=1
    author='hx'
    logic='40日动量'
    article='天风证券20170906–海外文献推荐015'
    freq='5mins'
    basic_datas = {'5mins': ['ret_close']}


    def st_factor(self):
        ret = self.database['5mins']['ret_close']
        ret = np.exp(dt_mean(ret, 48)) - 1
        return ret

    def result(self):
        res = self.cal_groupst()
        return res

if __name__ == '__main__':
    val1 = cal_factor(start=20210101, end=20210630)
