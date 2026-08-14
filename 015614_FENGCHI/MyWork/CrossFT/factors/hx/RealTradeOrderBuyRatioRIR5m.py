from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class RealTradeOrderBuyRatioRIR5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=6
    author='hx'
    logic='真实盘口成交与委托之比 行业排序与个股排序和'
    article=''
    freq='5mins'
    basic_datas = {'5mins': ['passivesellorderamt', 'activebuyorderamt', 'sellordercanceledamt',
                             'buytradeamt']}

    def st_factor(self):
        buy1 = self.database['5mins']['passivesellorderamt'] + self.database['5mins']['activebuyorderamt'] +\
              self.database['5mins']['sellordercanceledamt']
        buy2 = self.database['5mins']['buytradeamt']
        buy1 = dt_mean(buy1, 6)
        buy2 = dt_mean(buy2, 6)
        factor = (buy1 - buy2) / (buy1 + buy2)
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


