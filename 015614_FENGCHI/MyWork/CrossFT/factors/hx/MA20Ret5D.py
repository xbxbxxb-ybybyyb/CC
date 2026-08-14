from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np


class MA20Ret5D(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=25
    author='hx'
    logic='距离20日均线收益率5日均值'
    article=''
    freq='daily'
    basic_datas = {'daily': ['close_badj'],
                   '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        close = self.database['daily']['close_badj']
        factor = dt_mean(close / dt_mean(close, 20) - 1, 5)
        return factor

    def result(self):
        return self.cal_groupst()

if __name__=='__main__':
    f = MA20Ret5D()
    #print(f.result())
    f.save_result()