from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np


class UpPct5_5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=5
    author='hx'
    logic='成分股中上涨股数占比'
    article='银河证券 20140901 – 数量化择时'
    freq='5mins'
    basic_datas = {'5mins': ['ret_close']}

    def st_factor(self):
        ret = self.database['5mins']['ret_close']
        ret = (dt_mean(ret, 5) > 0).astype(int)
        return ret

    def result(self):
        return self.cal_groupst()

if __name__=='__main__':
    val1 = cal_factor(start=20210101, end=20210630)

