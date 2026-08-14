from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class StkIndCorrProdWgtRet(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=10
    author='hx'
    logic='个股滞后收益率与行业收益率相关系数与个股收益率的乘积，即领涨能力越强涨幅越大或者领涨能力越弱涨幅越小'
    article='长江证券-多因子选股（十四）：线性体系下的分域模型-211102'
    freq='5mins'
    basic_datas = {'5mins': ['ret_close', 'turn_total']}

    def st_factor(self):
        ret = self.database['5mins']['ret_close']
        turn = self.database['5mins']['turn_total']
        wgt_ret = dt_mean(ret * turn, 6) / dt_mean(turn, 6)
        return wgt_ret

    def cal_groupst(self):
        ret = self.st_factor()
        self.stgroup = sameshape(ret, self.group_factor())
        calfunc = self.group_func()
        ind = st2groupst(ret, self.stgroup, calfunc)
        corr = dt_corr2(dt_delay(ret, 6), ind, 240)
        factor = corr * ret
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def cal_customst(self):
        res = self.cal_groupst()
        return res

    def result(self):
        return self.cal_customst()

if __name__=='__main__':
    val1 = cal_factor()
