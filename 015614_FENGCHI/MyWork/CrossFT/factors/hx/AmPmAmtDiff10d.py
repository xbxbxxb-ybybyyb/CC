from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np


class AmPmAmtDiff10d(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=10
    author='hx'
    logic='上下午成交量离差10日均值'
    article=''
    freq='daily'
    basic_datas = {'1min': ['amt']}

    def st_factor(self):
        amt = self.database['1min']['amt']
        amt1 = np.nanmean(amt[:, :121], axis=1, keepdims=True)
        amt2 = np.nanmean(amt[:, 121:], axis=1, keepdims=True)
        factor = (amt1 - amt2) / (amt1 + amt2)
        factor = dt_mean(factor, 10)
        return factor

    def result(self):
        return self.cal_groupst()

if __name__=='__main__':
    f = AmPmAmtDiff10d()
    #print(f.result())
    f.save_result()