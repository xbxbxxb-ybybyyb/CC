from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class KDJRIR(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=40
    author='hx'
    logic='KDJ随机指标指标的个股排序与行业排序之和'
    article='广发证券-多因子Alpha系列报告之（四十二）：海量技术指标掘金Alpha因子-210730'
    freq='daily'
    basic_datas = {'daily': ['close_badj', 'high_badj', 'low_badj'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        close = self.database['daily']['close_badj']
        high = self.database['daily']['high_badj']
        low = self.database['daily']['low_badj']
        rsv = (close - dt_min(low, 9)) / (dt_max(high, 9) - dt_min(low, 9))
        k = dt_ewm(rsv, 3)
        d = dt_ewm(k, 3)
        return d

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
    val1 = cal_factor('data/user/015836/HANXU/jithub/crossft/factors/hx', 'KDJRIR_5m.py', {'daily': 1}, notrun=False)
