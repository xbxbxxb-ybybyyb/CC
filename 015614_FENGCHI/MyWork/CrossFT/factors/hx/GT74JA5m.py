from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class GT74JA5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=6
    author='hx'
    logic='GTJA74因子 个股排序与行业排序之和'
    article=''
    freq='5mins'
    basic_datas = {'5mins': ['adj_low', 'amt', 'adj_vol', 'adj_opn']}

    def st_factor(self):
        low = self.database['5mins']['adj_low']
        vol = self.database['5mins']['adj_vol']
        vwap = np.where(self.database['5mins']['adj_vol'] > 0,
                        self.database['5mins']['amt'] / self.database['5mins']['adj_vol'],
                        self.database['5mins']['adj_opn'])
        factor = cs_rank(dt_corr2(dt_mean(0.35 * low + 0.65 * vwap, 20), dt_mean(dt_mean(vol, 40), 20), 7)) + cs_rank(
            dt_corr2(cs_rank(vwap), cs_rank(vol), 6))
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
