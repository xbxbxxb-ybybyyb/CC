from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np


class DirectionVol(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=40
    author='hx'
    logic='过去40交易日波动率差'
    article='西南证券 20171221 – 基于方向波动率的选股因子研究'
    freq='daily'
    basic_datas = {'daily': ['pct_chg'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        ret = self.database['daily']['pct_chg'] / 100
        vol_dir = dt_std(zero_condition2(ret, ret), 40) - dt_std(zero_condition2(-ret, ret), 40)
        return vol_dir

    def result(self):
        return self.cal_groupst()

if __name__=='__main__':
    f = DirectionVol()
    #print(f.result())
    f.save_result()