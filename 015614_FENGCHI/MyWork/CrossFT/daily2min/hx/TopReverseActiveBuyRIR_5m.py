from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class TopReverseActiveBuyRIR_5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=1
    author='hx'
    logic='极端修正后的主动成交占比 个股排序与行业排序和'
    article='长江证券-基础因子研究（十四）：高频因子（九），高频波动中的时间序列信息-201012'
    freq='5mins'
    basic_datas = {'5mins': ['turn_total', 'ret_close']}

    def st_factor(self):
        turn = self.database['5mins']['turn_total']
        ret = (self.database['5mins']['ret_close'] / 1e2 + 0.1) / 0.1
        ret = ret.clip(0, 1)
        factor = dt_mean(turn * ret, 96) / dt_mean(turn, 96)
        factor = bottleneck.nanrankdata(factor, axis=-1) / np.sum(np.isfinite(factor), axis=-1, keepdims=True)
        factor = 0.01 / (0.99 * factor + 0.01) + 0.99 * factor + 0.01
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

