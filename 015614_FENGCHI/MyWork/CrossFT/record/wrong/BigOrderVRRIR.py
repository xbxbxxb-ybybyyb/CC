from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class BigOrderVRRIR(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=2
    author='hx'
    logic='大成交量下价量相关性 个股排序与行业排序和'
    article='广发证券-多因子Alpha系列报告之（四十一）：高频价量数据的因子化方法-210712 '
    freq='1min'
    basic_datas = {'1min': ['ret_close', 'turn_total']}

    def st_factor(self):
        ret = self.database['1min']['ret_close']
        turn = self.database['1min']['turn_total']
        factor = dt_corr2(zero_condition2(reducen(dt_rank(turn, 242), 0.7), ret),
                          zero_condition2(reducen(dt_rank(turn, 242), 0.7), turn),
                          242)
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
    val1 = cal_factor(numd={})
    val2 = cal_factor(numd={'1min': 10})
    gap = abs(val1 - val2)
    print(np.sum(np.where(np.isfinite(gap), gap, 0)))