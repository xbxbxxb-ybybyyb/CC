from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np

from scipy.stats import skew
class TurnSkew40d(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=40
    author='hx'
    logic='换手率偏度'
    article='兴业证券 (20160519):行业轮动系列专题报告. 基于不同市场情境下的行业轮动策略.'
    freq='daily'
    basic_datas = {'daily': ['turn'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        ts = self.database['daily']['turn']
        ts = dt_skew(ts, 40)
        return ts

    def result(self):
        return self.cal_groupst()

if __name__=='__main__':
    val1 = cal_factor(numd={})
    val2 = cal_factor(numd={'daily': 10})
    gap = abs(val1 - val2)
    print(np.nansum(gap))
