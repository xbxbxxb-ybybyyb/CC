from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class BigOrderDrivenRet(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=21
    author='hx'
    logic='过去20日日内大单驱动的收益率'
    article=''
    freq='daily'
    basic_datas = {'1min': ['vol', 'ret_close']}

    def st_factor(self):
        ret = self.database['1min']['ret_close']
        vol = self.database['1min']['vol']
        vol = bottleneck.nanrankdata(vol, axis=1)
        factor = np.nansum(np.where(vol > 120, ret, np.nan), axis=1, keepdims=True)
        factor = dt_mean(factor, 20)
        return factor

    def result(self):
        return self.cal_groupst()

if __name__=='__main__':
    f = BigOrderDrivenRet()
    #print(f.result())
    f.save_result()