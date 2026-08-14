from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class CancelRatioDiffRIR(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=2
    author='hx'
    logic='30分钟委买撤单额与主买成交额之比减去委卖撤单额与主卖成交额之比 个股排序与行业排序之和'
    article=''
    freq='5mins'
    basic_datas = {'5mins': ['buytradeamt', 'selltradeamt', 'buyordercanceledamt', 'sellordercanceledamt']}

    def st_factor(self):
        buytradeamt = dt_mean(self.database['5mins']['buytradeamt'], 6)
        selltradeamt = dt_mean(self.database['5mins']['selltradeamt'], 6)
        buyordercanceledamt = dt_mean(self.database['5mins']['buyordercanceledamt'], 6)
        sellordercanceledamt = dt_mean(self.database['5mins']['sellordercanceledamt'], 6)
        factor = buyordercanceledamt / buytradeamt - sellordercanceledamt / selltradeamt
        factor[(buytradeamt == 0) | (selltradeamt == 0)] = np.nan
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

