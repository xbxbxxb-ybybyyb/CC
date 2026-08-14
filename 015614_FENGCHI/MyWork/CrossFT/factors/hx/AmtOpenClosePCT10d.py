from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np


class AmtOpenClosePCT10d(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=10
    author='hx'
    logic='过去10日开盘半小时成交额与收盘半小时成交额差比和'
    article=''
    freq='daily'
    basic_datas = {'5mins': ['amt']}

    def st_factor(self):
        amt = self.database['5mins']['amt']
        amt1 = np.nanmean(amt[:, :6], axis=1, keepdims=True)
        amt2 = np.nanmean(amt[:, -6:], axis=1, keepdims=True)
        factor = (amt1 - amt2) / (amt1 + amt2)
        factor = dt_mean(factor, 10)
        return factor

    def result(self):
        return self.cal_groupst()

if __name__=='__main__':
    f = AmtOpenClosePCT10d()
    #print(f.result())
    f.save_result()