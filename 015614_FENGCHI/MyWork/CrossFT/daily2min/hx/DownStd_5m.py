from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossFactor import crossFactor
import numpy as np
from basic.operators import *


class DownStd_5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=40
    author='hx'
    logic='40日下行波动率'
    article='兴业证券20200730–海外文献推荐系列087'
    freq='5mins'
    basic_datas = {'5mins': ['ret_close']}


    def st_factor(self):
        ret = self.database['5mins']['ret_close']
        return ret

    def cal_groupst(self):
        ret = self.st_factor()
        self.group = sameshape(ret, self.group_factor())
        self.func = self.group_func()
        ret = st2groupst(ret, self.group, self.func)
        ret = dt_std(zero_condition2(ret, ret), 40)
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.cal_groupst()

if __name__ == '__main__':
    val1 = cal_factor(start=20210101, end=20210630)
