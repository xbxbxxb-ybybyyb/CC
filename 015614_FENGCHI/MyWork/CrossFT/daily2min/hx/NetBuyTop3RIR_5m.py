from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class NetBuyTop3RIR_5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=10
    author='hx'
    logic='过去10日净流入排名+净流入行业Top3股票平均流入排名'
    article=''
    freq='5mins'
    basic_datas = {'5mins': ['turn_trade_sell', 'turn_trade_buy']}

    def st_factor(self):
        factor = self.database['5mins']['turn_trade_buy'] - self.database['5mins']['turn_trade_sell']
        factor = dt_mean(factor, 48)
        return factor

    def cal_groupst(self):
        factor = self.st_factor()
        stgroup = sameshape(factor, self.group_factor())
        groups = np.unique(stgroup[np.isfinite(stgroup)])
        shape = factor.shape
        rank = np.full(factor.shape, np.nan)
        for g in groups:
            val = stgroup == g
            rank = np.where(val, bottleneck.nanrankdata(np.where(val, -factor, np.nan), axis=len(shape) - 1), rank)
        factor[rank > 3] = np.nan
        group = sameshape(factor, self.group_factor())
        groups = np.unique(group[np.isfinite(group)])
        res = np.full(factor.shape[:-1] + (len(groups),), np.nan)
        for j, g in enumerate(groups):
            res[..., j] = self.group_func()(np.where(group == g, factor, np.nan), axis=-1)
        res = bottleneck.nanrankdata(res, axis=-1) / np.sum(np.isfinite(res), axis=-1, keepdims=True)
        res2 = np.full(factor.shape, np.nan)
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
        return self.cal_groupst()


if __name__ == '__main__':
    val1 = cal_factor(start=20210101, end=20210630)
