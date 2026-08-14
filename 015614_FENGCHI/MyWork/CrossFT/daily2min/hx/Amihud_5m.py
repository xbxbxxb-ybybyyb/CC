from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np


class Amihud_5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=20
    author='hx'
    logic='单位成交额的收益率'
    article='兴业证券 (20160519):行业轮动系列专题报告. 基于不同市场情境下的行业轮动策略.'
    freq='5mins'
    basic_datas = {'5mins': ['ret_close', 'turn_total']}

    def st_factor(self):
        ah = self.database['5mins']['ret_close'] / self.database['5mins']['turn_total'] * 1e4
        ah = div2(dt_mean(ah, 20) , dt_std(ah, 20))
        return ah

    def result(self):
        return self.cal_groupst()

if __name__=='__main__':
    val1 = cal_factor(start=20210101, end=20210630)
