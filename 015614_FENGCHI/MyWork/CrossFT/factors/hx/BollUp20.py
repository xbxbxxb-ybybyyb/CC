from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np


class BollUp20(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=20
    author='hx'
    logic='突破上轨股票数量占比'
    article='银河证券 (20160506):量化策略. 基于公募基金仓位测算的市场择时策略'
    freq='daily'
    basic_datas = {'daily': ['close_badj'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        pr = self.database['daily']['close_badj']
        up = pr > dt_mean(pr, 20) + dt_std(pr, 20)
        return up

    def result(self):
        return self.cal_groupst()

if __name__=='__main__':
    val1 = cal_factor(numd={})
    val2 = cal_factor(numd={'daily': 10})
    gap = abs(val1 - val2) / abs(val1)
    print(np.nansum(gap))
