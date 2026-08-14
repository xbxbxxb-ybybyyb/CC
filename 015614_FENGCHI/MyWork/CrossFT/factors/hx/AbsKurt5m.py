from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class AbsKurt5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=10
    author='hx'
    logic='5分钟收益对行业收益率回归的残差的峰度'
    article='财通证券-“星火”多因子专题报告（九）：博彩偏好还是风险补偿？高频特质偏度因子全解析-191210'
    freq='5mins'
    basic_datas = {'daily': [], '30mins': [], '5mins': ['ret_close'], '1min': []}

    def st_factor(self):
        ret = self.database['5mins']['ret_close']
        return ret

    def cal_groupst(self):
        ret = self.st_factor()
        group = sameshape(ret, self.group_factor())
        res = st2groupst(ret, group, self.group_func())
        skew = dt_resid2(res, ret, 240)
        skew = dt_kurt(skew, 240)
        return arr_match_index(skew, self.cal_date_range, self.date_range)

    def cal_customst(self):
        res = self.cal_groupst()
        return res

    def result(self):
        return self.cal_customst()

if __name__=='__main__':

    val1 = cal_factor()
