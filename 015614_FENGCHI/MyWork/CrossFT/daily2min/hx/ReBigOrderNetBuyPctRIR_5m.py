from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class ReBigOrderNetBuyPctRIR_5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=6
    author='hx'
    logic='大单净买入占比 行业排序与个股排序和'
    article='研究报告：海通证券-选股因子系列研究（七十二）：大单的精细化处理与大单因子重构-210120'
    freq='5mins'
    basic_datas = {'5mins': ['turn_order_active_buy', 'turn_order_active_sell']}

    def st_factor(self):
        buy = self.database['5mins']['turn_order_active_buy']
        sell = self.database['5mins']['turn_order_active_sell']
        lb = np.log(1000 * (1 + buy - sell))
        limit = dt_mean(lb, 240) + dt_std(lb, 240)
        factor = dt_mean(np.where(lb > limit, buy - sell, 0), 48)
        return factor

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
    val1 = cal_factor(start=20210101, end=20210630)
