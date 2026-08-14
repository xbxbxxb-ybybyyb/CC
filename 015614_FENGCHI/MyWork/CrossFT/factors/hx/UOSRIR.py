from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class UOSRIR(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=60
    author='hx'
    logic='UOS终极波动指标 个股排序与行业排序和'
    article='广发证券-多因子Alpha系列报告之（四十二）：海量技术指标掘金Alpha因子-210730'
    freq='daily'
    basic_datas = {'daily': ['close_badj', 'high_badj', 'low_badj']}

    def st_factor(self):
        close = self.database['daily']['close_badj']
        high = self.database['daily']['high_badj']
        low = self.database['daily']['low_badj']
        th = dt_max(high - dt_delay(close, 1), 20)
        tl = dt_min(low - dt_delay(close, 1), 20)
        acc1 = (close - dt_mean(tl, 10) * 10) / (dt_mean(th - tl, 10) * 10)
        acc2 = (close - dt_mean(tl, 20) * 20) / (dt_mean(th - tl, 20) * 20)
        acc3 = (close - dt_mean(tl, 30) * 30) / (dt_mean(th - tl, 30) * 30)
        uos = (acc1 * 6 + acc2 * 3 + acc3 * 2) / 11
        return uos

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
