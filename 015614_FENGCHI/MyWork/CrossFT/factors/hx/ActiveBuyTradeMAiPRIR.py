from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class ActiveBuyTradeMAiPRIR(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=12
    author='hx'
    logic='5分钟主买成交额长短均线的交点个数 个股排序与行业排序之和'
    article=''
    freq='5mins'
    basic_datas = {'5mins': ['buytradeamt']}

    def st_factor(self):
        pr = self.database['5mins']['buytradeamt']
        ma5 = dt_mean(pr, 5)
        ma20 = dt_mean(pr, 20)
        point = dt_mean(((ma5 - ma20) * dt_delay(ma5 - ma20, 1) <= 0).astype('float32'), 48)
        return point

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

