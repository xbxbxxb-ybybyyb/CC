from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np


class MaxDownPct(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=10
    author='hx'
    logic='下影线长度占总K线长度之比'
    article=''
    freq='daily'
    basic_datas = {'daily': ['close_badj', 'open_badj', 'high_badj', 'low_badj'],
                   '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        close = self.database['daily']['close_badj']
        opn = self.database['daily']['open_badj']
        high = self.database['daily']['high_badj']
        low = self.database['daily']['low_badj']
        factor = dt_mean((np.fmin(opn, close) - low) / (high - low), 10)
        return factor

    def result(self):
        return self.cal_groupst()

if __name__=='__main__':
    f = MaxDownPct()
    #print(f.result())
    f.save_result()