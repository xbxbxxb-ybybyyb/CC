from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np


class Skew1Y_5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=244
    author='hx'
    logic='行业过去1年收益率偏度'
    article='兴业证券 20140630 – 行业配置系列研究之一'
    freq='5mins'
    basic_datas = {'5mins': ['ret_close']}

    def st_factor(self):
        ret = self.database['5mins']['ret_close']
        return ret

    def cal_groupst(self):
        self.factor = self.st_factor()
        self.stgroup = sameshape(self.factor, self.group_factor())
        calfunc = self.group_func()
        res = st2groupst(self.factor, self.stgroup, calfunc)
        res = dt_skew(res, 244)
        return arr_match_index(res, self.cal_date_range, self.date_range)

    def result(self):
        return self.cal_groupst()

if __name__=='__main__':
    val1 = cal_factor(start=20210101, end=20210630)
