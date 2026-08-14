from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
from xquant.factordata import FactorData
import numpy as np
import bottleneck
fd = FactorData()

def cs_residual3(y, x1, x2):
    finite = np.isfinite(y) & np.isfinite(x1) & np.isfinite(x2)
    finite_code = finite.sum(axis=2)
    y = y.copy()
    x1 = x1.copy()
    x2 = x2.copy()
    y[~ finite] = 0
    x1[~ finite] = 0
    x2[~ finite] = 0
    y -= (y.sum(axis=2) / finite_code)[..., None]
    y /= ((y ** 2).sum(axis=2) ** 0.5)[..., None]
    x1 -= (x1.sum(axis=2) / finite_code)[..., None]
    x1 /= ((x1 ** 2).sum(axis=2) ** 0.5)[..., None]
    x2 -= (x2.sum(axis=2) / finite_code)[..., None]
    x2 /= ((x2 ** 2).sum(axis=2) ** 0.5)[..., None]
    b12 = (x1 * x2).sum(axis=2)[..., None]
    e12 = x1 - b12 * x2
    e12 /= ((e12 ** 2).sum(axis=2) ** 0.5)[..., None]
    res = y - e12 * (y * e12).sum(axis=2)[..., None] - x2 * (y * x2).sum(axis=2)[..., None]
    return res

class SmallAmtIndResidual(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=10
    author='hx'
    logic='小单成交额对行业平均市值和成交额回归的残差'
    article='长江证券-基础因子研究（五）：谁是“聪明钱”？资金流因子全面测试兼正交化方法详解-180611'
    freq='daily'
    basic_datas = {'daily': ['amt', 'mkt_cap_ard']}

    def st_factor(self):
        small_amt = fd.get_factor_value('Basic_factor', [trans_int2windcode(x) for x in self.code_list],
                                        [str(x) for x in self.cal_date_range], ['buy_value_small_order'])
        small_amt = small_amt.iloc[:, 0].unstack()
        small_amt.index = small_amt.index.map(int)
        small_amt.columns = small_amt.columns.map(trans_windcode2int)
        small_amt = small_amt.reindex(self.cal_date_range, self.code_list).values[:, None]
        small_amt = np.log(small_amt)
        return small_amt

    def cal_groupst(self):
        amt = np.log(self.database['daily']['amt'] * 10)
        mkt_cap_ard = np.log(self.database['daily']['mkt_cap_ard'] * 10)
        group = sameshape(amt, self.group_factor())
        amt = st2groupst(amt, group, self.group_func())
        mkt_cap_ard = st2groupst(mkt_cap_ard, group, self.group_func())
        return amt, mkt_cap_ard

    def cal_customst(self):
        small_amt = self.st_factor()
        amt, mkt_cap_ard = self.cal_groupst()
        res = cs_residual3(small_amt, amt, mkt_cap_ard)
        res = dt_mean(res, 10)
        res = arr_match_index(res, self.cal_date_range, self.date_range)
        return res

    def result(self):
        return self.cal_customst()

if __name__=='__main__':
    val1 = cal_factor()
