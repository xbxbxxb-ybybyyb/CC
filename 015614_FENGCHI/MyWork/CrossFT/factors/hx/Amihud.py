from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np


class Amihud(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=20
    author='hx'
    logic='单位成交额的收益率'
    article='兴业证券 (20160519):行业轮动系列专题报告. 基于不同市场情境下的行业轮动策略.'
    freq='daily'
    basic_datas = {'daily': ['pct_chg', 'amt'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        ah = self.database['daily']['pct_chg'] / self.database['daily']['amt'] * 1e4
        ah = div2(dt_mean(ah, 20) , dt_std(ah, 20))
        return ah

    def result(self):
        return self.cal_groupst()

if __name__=='__main__':
    val1 = cal_factor(numd={})
    val2 = cal_factor(numd={'daily': 15})
    gap = abs(val1 - val2)
    print(np.sum(np.where(np.isfinite(gap), gap, 0)))