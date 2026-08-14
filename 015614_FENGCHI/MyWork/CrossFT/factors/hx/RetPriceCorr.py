from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class RetPriceCorr(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=5
    author='hx'
    logic='过去5日日内收益率与价格的相关系数'
    article=''
    freq='5mins'
    basic_datas = {'5mins': ['adj_close']}

    def st_factor(self):
        adj_close = self.database['5mins']['adj_close']
        ret = dt_pct(adj_close, 1)
        corr = dt_corr2(adj_close, ret, 120)
        return corr

    def result(self):
        return self.cal_groupst()

if __name__=='__main__':
    val1 = cal_factor(numd={'5mins': 20})
    val2 = cal_factor(numd={'5mins': 15})
    gap = abs(val1 - val2)
    print(np.sum(np.where(np.isfinite(gap), gap, 0)))
