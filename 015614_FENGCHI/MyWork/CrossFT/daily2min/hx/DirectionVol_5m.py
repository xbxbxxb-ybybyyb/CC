from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np


class DirectionVol_5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=40
    author='hx'
    logic='过去40交易日波动率差'
    article='西南证券 20171221 – 基于方向波动率的选股因子研究'
    freq='5mins'
    basic_datas = {'5mins': ['ret_close']}

    def st_factor(self):
        ret = self.database['5mins']['ret_close'] / 100
        vol_dir = dt_std(zero_condition2(ret, ret), 40) - dt_std(zero_condition2(-ret, ret), 40)
        return vol_dir

    def result(self):
        return self.cal_groupst()

if __name__=='__main__':
    val1 = cal_factor(start=20210101, end=20210630)
