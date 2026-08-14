from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
from scipy.stats import norm
import numpy as np
import bottleneck

class Asym5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=12
    author='hx'
    logic='收益率的概率密度函数和分布函数的相关系数 个股排序与行业排序之和'
    article=''
    freq='5mins'
    basic_datas = {'5mins': ['ret_close']}

    def st_factor(self):
        r = self.database['5mins']['ret_close']
        n = 240
        m = dt_mean(r, n)
        s = dt_std(r, n)
        s[~ np.isfinite(s)] = np.nan
        h = 1.06 * s * n ** (-0.2)
        cdf = norm.cdf((1.5 - (r - m) / s) / h)
        pdf = norm.pdf((1.5 - (r - m) / s) / h)
        factor = dt_corr2(cdf, pdf, 12)
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
