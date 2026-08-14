from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class ActivePassiveRetDiff(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=21
    author='hx'
    logic='过去20日主动与被动收益率之差'
    article=''
    freq='daily'
    basic_datas = {'1min': ['turn_order_active', 'ret_close']}

    def st_factor(self):
        ret = self.database['1min']['ret_close']
        active = self.database['1min']['turn_order_active']
        active = bottleneck.nanrankdata(active, axis=1)
        factor = np.nansum(np.where(active > 120, ret, np.nan), axis=1, keepdims=True) - np.nansum(
            np.where(active <= 120, ret, np.nan), axis=1, keepdims=True)
        factor = dt_mean(factor, 20)
        return factor

    def result(self):
        return self.cal_groupst()

if __name__=='__main__':
    f = ActivePassiveRetDiff()
    #print(f.result())
    f.save_result()