from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class BGSRIR_5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=20
    author='hx'
    logic='基于凸显理论的ST因子的个股排序与行业排序之和'
    article='广发证券-行为金融因子研究之三：结合凸显理论的选股研究-180130'
    freq='5mins'
    basic_datas = {'5mins': ['ret_close']}


    def st_factor(self):
        r = self.database['5mins']['ret_close'] / 100
        rm = np.nanmean(r, axis=2, keepdims=True)
        sigma = np.abs(r - rm) / (np.abs(r) + np.abs(rm) + 0.9) * np.exp(r - rm)
        gamma = bottleneck.nanrankdata(sigma, axis=2)
        w = gamma / dt_mean(gamma, 10)
        st = dt_mean(w * r, 10) - dt_mean(r, 10)
        # st = gamma
        return st

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

