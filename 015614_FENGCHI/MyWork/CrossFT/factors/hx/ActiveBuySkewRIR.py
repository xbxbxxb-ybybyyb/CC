from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class ActiveBuySkewRIR(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=5
    author='hx'
    logic='主动买入成交量日内偏度 个股排序与行业排序之和'
    article=''
    freq='daily'
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': ['turn_trade_buy']}

    def st_factor(self):
        x = self.database['1min']['turn_trade_buy']
        n = np.isfinite(x)
        x[~ n] = 0
        n = n.astype('float32')
        x2 = x ** 2
        x3 = x ** 3
        cn = n.sum(axis=1)
        cx = x.sum(axis=1)
        cx2 = x2.sum(axis=1)
        cx3 = x3.sum(axis=1)
        const = (cn * (cn - 1)) ** 0.5 / (cn - 2)
        skew = const * (cn * cx3 - 3 * cx * cx2 + 2 * cx ** 3 / cn
                        ) / (cn ** 2 * cx2 - cn * cx ** 2) ** 1.5
        skew[cn < 5] = np.nan
        skew = skew[:, None]
        return skew

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