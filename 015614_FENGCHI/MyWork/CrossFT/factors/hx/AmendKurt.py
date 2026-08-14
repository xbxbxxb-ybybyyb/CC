from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np


class AmendKurt(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=40
    author='hx'
    logic='过去40交易日修正峰度'
    article='西南证券 20171221 – 基于方向波动率的选股因子研究'
    freq='daily'
    basic_datas = {'daily': ['pct_chg'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        ret = self.database['daily']['pct_chg'] / 100
        vol_dir = dt_std(zero_condition2(ret, ret), 40) - dt_std(zero_condition2(-ret, ret), 40)
        skew = dt_kurt(ret, 40) * dt_std(ret, 40) ** 2 / vol_dir ** 2
        return skew

    def result(self):
        return self.cal_groupst()

if __name__=='__main__':
    f = AmendKurt()
    #print(f.result())
    f.save_result()