from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np


class Skew1Y(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=244
    author='hx'
    logic='行业过去1年收益率偏度'
    article='兴业证券 20140630 – 行业配置系列研究之一'
    freq='daily'
    basic_datas = {'daily': ['pct_chg'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        ret = self.database['daily']['pct_chg']
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
    f = Skew1Y()
    #print(f.result())
    f.save_result()