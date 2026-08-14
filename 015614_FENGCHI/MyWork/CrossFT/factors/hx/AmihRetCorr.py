from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class AmihRetCorr(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days = 4
    author='hx'
    logic='过去5日日内收益率与振幅的相关系数'
    article=''
    freq='5mins'
    basic_datas = {'5mins': ['adj_close', 'adj_high', 'adj_low']}

    def st_factor(self):
        adj_close = self.database['5mins']['adj_close']
        adj_high = self.database['5mins']['adj_high']
        adj_low = self.database['5mins']['adj_low']
        ret = dt_pct(adj_close, 1)
        amih = (adj_high - adj_low) / adj_close
        corr = dt_corr2(amih, ret, 120)
        return corr

    def result(self):
        return self.cal_groupst()

if __name__=='__main__':
    val1 = cal_factor(numd={})
    val2 = cal_factor(numd={'daily': 10})
    gap = abs(val1 - val2)
    print(np.sum(np.where(np.isfinite(gap), gap, 0)))
