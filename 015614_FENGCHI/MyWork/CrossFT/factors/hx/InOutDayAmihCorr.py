from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class InOutDayAmihCorr(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=12
    author='hx'
    logic='日内与日间单位成交额振幅的相关系数 个股排序与行业排序之和'
    article=''
    freq='5mins'
    basic_datas = {'5mins': ['close', 'amt'], 'daily': ['pre_close', 'pct_chg', 'amt']}

    def st_factor(self):
        ret1 = self.database['5mins']['close'] / self.database['daily']['pre_close'] - 1
        ret2 = ds_delay(self.database['daily']['pct_chg'].repeat(48, axis=1), 1)
        amt1 = ts_cumsum(self.database['5mins']['amt'])
        amt2 = ds_delay(self.database['daily']['amt'].repeat(48, axis=1), 1)
        amih1 = abss(ret1) / amt1 * 1e8
        amih2 = abss(ret2) / amt2 * 1e8
        factor = ds_corr2(amih1, amih2, 10)
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
    val1 = cal_factor()

