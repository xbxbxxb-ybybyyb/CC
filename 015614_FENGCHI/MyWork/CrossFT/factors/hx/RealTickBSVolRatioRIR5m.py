from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class RealTickBSVolRatioRIR5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=6
    author='hx'
    logic='真实盘口新增委托量的买卖之比 行业排序与个股排序和'
    article=''
    freq='5mins'
    basic_datas = {'5mins': ['passivesellordervol', 'activebuyordervol', 'sellordercanceledvol',
                             'passivebuyordervol', 'activesellordervol', 'buyordercanceledvol']}

    def st_factor(self):
        buy = self.database['5mins']['passivesellordervol'] + self.database['5mins']['activebuyordervol'] +\
              self.database['5mins']['sellordercanceledvol']
        sell = self.database['5mins']['passivebuyordervol'] + self.database['5mins']['activesellordervol'] +\
              self.database['5mins']['buyordercanceledvol']
        buy = dt_mean(buy, 6)
        sell = dt_mean(sell, 6)
        factor = (buy - sell) / (buy + sell)
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


