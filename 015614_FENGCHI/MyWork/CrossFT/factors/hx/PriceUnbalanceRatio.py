from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np


class PriceUnbalanceRatio(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=10
    author='hx'
    logic='过去10日日内分时价格的不平衡度'
    article=''
    freq='daily'
    basic_datas = {'1min': ['close', 'amt']}

    def st_factor(self):
        close = self.database['1min']['close']
        amt = self.database['1min']['amt']
        pr1 = np.nanmean(close, axis=1, keepdims=True)
        amt[~np.isfinite(close)] = np.nan
        pr2 = np.nansum(close * amt, axis=1, keepdims=True) / np.nansum(amt, axis=1, keepdims=True)
        factor = dt_mean(pr1 / pr2, 10)
        return factor

    def result(self):
        return self.cal_groupst()

if __name__=='__main__':
    f = PriceUnbalanceRatio()
    #print(f.result())
    f.save_result()