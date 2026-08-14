from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class BigAmihPrRatio5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=20
    author='hx'
    logic='大Amih下的vwap比整体vwap 个股排序与行业排序之和'
    article='跟踪聪明钱：从分钟行情数据到选股因子_方正证券'
    freq='5mins'
    basic_datas = {'5mins': ['ret_close', 'adj_amt', 'adj_vol']}


    def st_factor(self):
        ret = self.database['5mins']['ret_close']
        amt = self.database['5mins']['adj_amt']
        vol = self.database['5mins']['adj_vol']
        amih = dt_rank(abss(ret) / vol, 96) > 0.8
        vwap1 = dt_mean(amt, 48) / dt_mean(vol, 48)
        vwap2 = dt_mean(np.where(amih, amt, 0), 48) / dt_mean(np.where(amih, vol, 0), 48)
        factor = vwap2 / vwap1
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

