from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class LSVRIR(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=10
    author='hx'
    logic='用被动单作为对手方主动单计算的羊群效应 行业排序与个股排序和'
    article='广发证券-高频数据因子研究系列三：基于个股羊群效应的选股因子研究-200505'
    freq='5mins'
    basic_datas = {'5mins': ['turn_order_passive_sell', 'turn_order_passive_buy']}

    def st_factor(self):
        sell = self.database['5mins']['turn_order_passive_buy']
        buy = self.database['5mins']['turn_order_passive_sell']
        lsv = div2(dt_mean(buy, 6) , (dt_mean(buy, 6) + dt_mean(sell, 6)))
        return lsv

    def cal_groupst(self):
        indicator = self.st_factor()
        group = sameshape(indicator, self.group_factor())
        groups = np.unique(group[np.isfinite(group)])
        res = np.full(indicator.shape[:-1] + (len(groups),), np.nan)
        for j, g in enumerate(groups):
            res[..., j] = self.group_func()(np.where(group == g, indicator, np.nan), axis=-1)
        res = bottleneck.nanrankdata(res, axis=-1) / np.sum(np.isfinite(res), axis=-1, keepdims=True)
        res2 = np.full(indicator.shape, np.nan)
        for j, g in enumerate(groups):
            res2 = np.where(group == g, res[..., [j]], res2)
        return arr_match_index(res2, self.cal_date_range, self.date_range)

    def cal_customst(self):
        factor = self.st_factor()
        factor = bottleneck.nanrankdata(factor, axis=-1) / np.sum(np.isfinite(factor), axis=-1, keepdims=True)
        factor = arr_match_index(factor, self.cal_date_range, self.date_range)
        res = self.cal_groupst()
        return factor + res

    def result(self):
        return self.cal_customst()
if __name__=='__main__':
    val1 = cal_factor(numd={})
    val2 = cal_factor(numd={'5mins': 15})
    gap = abs(val1 - val2)
    print(np.sum(np.where(np.isfinite(gap), gap, 0)))
