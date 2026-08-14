from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class MomUnderDealRIR_5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=5
    author='hx'
    logic='每笔成交量较小与较大时的收益差 个股排序与行业排序和'
    article='长江证券-基础因子研究（十七）：高频因子（十一），高频数据的微观划分-210322 '
    freq='5mins'
    basic_datas = {'5mins': ['ret_close', 'vol', 'num_total']}

    def st_factor(self):
        ret = self.database['5mins']['ret_close']
        deal = self.database['5mins']['vol'] / self.database['5mins']['num_total']
        rank = dt_rank(deal, 48)
        ret1 = dt_mean(np.where(rank < 0.2, ret, 0), 48)
        ret2 = dt_mean(np.where(rank > 0.8, ret, 0), 48)
        return ret1 - ret2

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

