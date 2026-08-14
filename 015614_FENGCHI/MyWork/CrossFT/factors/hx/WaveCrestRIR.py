from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class WaveCrestRIR(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=21
    author='hx'
    logic='波峰因子 行业排序与个股排序和'
    article='长江证券-基础因子研究（十八）：高频因子（十二），日内与日间-210606'
    freq='daily'
    basic_datas = {'1min': ['turn_total']}

    def st_factor(self):
        turn = self.database['1min']['turn_total']
        turn_mean = np.nanmean(turn, axis=1, keepdims=True)
        turn_std = np.nanstd(turn, axis=1, keepdims=True)
        factor = np.sum(turn > turn_mean + turn_std, axis=1, keepdims=True)
        factor = dt_mean(factor, 21)
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
    f = WaveCrestRIR()
    #print(f.result())
    f.save_result()

