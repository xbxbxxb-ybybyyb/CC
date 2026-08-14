from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class RankAmih5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=6
    author='hx'
    logic='利用行业关系的改进amih因子'
    article='20210902-东方证券-因子选股系列研究之七十八：存在于全市场范围内的稳健动量效应'
    freq='5mins'
    basic_datas = {'5mins': ['ret_close', 'turn_total']}

    def st_factor(self):
        ret = np.fabs(self.database['5mins']['ret_close'] / self.database['5mins']['turn_total'])
        ret[self.database['5mins']['turn_total'] == 0] = np.nan
        return ret

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
        return res2

    def cal_customst(self):
        factor = self.st_factor()
        factor = bottleneck.nanrankdata(factor, axis=-1) / np.sum(np.isfinite(factor), axis=-1, keepdims=True)
        # factor = arr_match_index(factor, self.cal_date_range, self.date_range)
        res = self.cal_groupst()
        return factor + res

    def result(self):
        factor = self.cal_customst()
        factor = dt_mean(factor, 480)
        factor = arr_match_index(factor, self.cal_date_range, self.date_range)
        return factor

if __name__=='__main__':
    val1 = cal_factor()

