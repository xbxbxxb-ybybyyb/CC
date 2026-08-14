from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class MAOLSRIR(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=62
    author='hx'
    logic='MA均价线性回归系数的个股排序与行业排序之和'
    article='广发证券-多因子Alpha系列报告之（四十二）：海量技术指标掘金Alpha因子-210730'
    freq='daily'
    basic_datas = {'daily': ['close_badj'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        close = self.database['daily']['close_badj']
        ma = dt_mean(close, 6)
        mean = dt_mean(ma, 6)
        factor = (2.5 * (ma - mean) + 1.5 * (dt_delay(ma, 1) - mean) + 0.5 * (dt_delay(ma, 2) - mean) -
                  0.5 * (dt_delay(ma, 3) - mean) - 1.5 * (dt_delay(ma, 4) - mean) - 2.5 * (dt_delay(ma, 5) - mean))
        factor = factor / ma
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
    val1 = cal_factor(numd={})
    val2 = cal_factor(numd={'daily': 15})
    gap = abs(val1 - val2)
    print(np.sum(np.where(np.isfinite(gap), gap, 0)))