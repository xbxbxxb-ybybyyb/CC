from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class MAPctRIR_5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=20
    author='hx'
    logic='距MA20差异率的个股排序与行业排序之和'
    article='银河证券 (20160506):量化策略. 基于公募基金仓位测算的市场择时策略'
    freq='5mins'
    basic_datas = {'5mins': ['close_badj']}

    def st_factor(self):
        pr = self.database['5mins']['close_badj']
        pct = pr / dt_mean(pr, 20) - 1
        return pct

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
