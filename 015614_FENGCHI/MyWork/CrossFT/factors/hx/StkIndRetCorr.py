from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class StkIndRetCorr(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=6
    author='hx'
    logic='个股收益率与行业收益率的相关系数'
    article=''
    freq='5mins'
    basic_datas = {'5mins': ['ret_close']}

    def st_factor(self):
        ret_close = self.database['5mins']['ret_close']
        return ret_close

    def cal_groupst(self):
        indicator = self.database['5mins']['ret_close']
        group = sameshape(indicator, self.group_factor())
        res = st2groupst(indicator, group, self.group_func())
        return res

    def cal_customst(self):
        factor = self.st_factor()
        res = self.cal_groupst()
        factor = dt_corr2(factor, res, 48)
        factor = arr_match_index(factor, self.cal_date_range, self.date_range)
        return factor

    def result(self):
        return self.cal_customst()

if __name__=='__main__':
    val1 = cal_factor()


