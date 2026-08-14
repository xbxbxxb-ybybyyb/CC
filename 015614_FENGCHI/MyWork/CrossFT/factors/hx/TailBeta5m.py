from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
from scipy.stats import norm
import numpy as np
import bottleneck

def dt_beta2(x, y, m3):
    x = x.copy()
    y = y.copy()
    ar = ArrReshape()
    x = ar.to2d(x)
    y = ar.to2d(y)
    f = np.isfinite(x) & np.isfinite(y)
    x[~ f] = 0
    y[~ f] = 0
    cx = bottleneck.move_sum(x, m3, axis=0)
    cy = bottleneck.move_sum(y, m3, axis=0)
    cx2 = bottleneck.move_sum(x ** 2, m3, axis=0)
    cxy = bottleneck.move_sum(x * y, m3, axis=0)
    cn = bottleneck.move_sum(f.astype('float32'), m3, axis=0)
    a = (cn * cxy - cx * cy)
    b = (cn * cx2 - cx ** 2)
    beta = np.divide(a, b, out=np.full(x.shape, np.nan), where=abs(b) > 1e-8)
    beta[cn < 3] = np.nan
    return ar.to3d(beta)

class TailBeta5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=21
    author='hx'
    logic='极端下跌时的beta 个股排序与行业排序之和'
    article=''
    freq='5mins'
    basic_datas = {'5mins': ['ret_close']}

    def st_factor(self):
        r = self.database['5mins']['ret_close']
        m = np.nanmedian(r, axis=2, keepdims=True)
        m[dt_rank(m, 240) > 0.05] = np.nan
        m = m.repeat(r.shape[2], axis=2)
        factor = dt_beta2(r, m, 240)
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
