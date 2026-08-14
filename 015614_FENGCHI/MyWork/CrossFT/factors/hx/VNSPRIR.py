from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class VNSPRIR(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=101
    author='hx'
    logic='卖出倾向因子(VNSP)因子的个股排序与行业排序之和'
    article='广发证券-行为金融因子研究之四：基于V型处置效应的选股策略研究-190307'
    freq='daily'
    basic_datas = {'daily': ['close_badj', 'turn'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        close = self.database['daily']['close_badj']
        turn = self.database['daily']['turn'] / 100
        res = np.empty_like(close)
        res[:100] = np.nan
        for j in range(100, close.shape[0]):
            ret = close[[j]] / close[j-99:j+1] - 1
            ret = np.where(ret < 0, - ret, 0)
            wgt = np.nancumprod(1 - turn[j:j-100:-1], axis=0)[::-1] * turn[j-99:j+1] / (1 - turn[j-99:j+1])
            wgt = wgt / np.nansum(wgt, axis=0, keepdims=True)
            res[j] = np.nansum(wgt * ret, axis=0)
        return res

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
    val1 = cal_factor('data/user/015836/HANXU/jithub/crossft/factors/hx', 'VNSPRIR_5m.py', {'daily': 1}, notrun=False)
