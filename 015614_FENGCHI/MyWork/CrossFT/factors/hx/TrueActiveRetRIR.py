from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class TrueActiveRetRIR(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=5
    author='hx'
    logic='距离近期筹码中心点的收益率 减去行业指数距离筹码中心点的收益率'
    article=''
    freq='5mins'
    basic_datas = {'5mins': ['adj_close']}

    def st_factor(self):
        adj_close = self.database['5mins']['adj_close']
        mean = dt_mean(adj_close, 240)
        med = dt_median(adj_close, 240)
        mode = 3 * med - 2 * mean
        factor = adj_close / mode - 1
        return factor

    def cal_groupst(self):
        indicator = dt_pct(self.database['5mins']['adj_close'], 1)
        group = sameshape(indicator, self.group_factor())
        res = st2groupst(indicator, group, self.group_func())
        res = np.nancumprod(1 + indicator.reshape(-1, res.shape[-1]), axis=0).reshape(res.shape)
        mean = dt_mean(res, 240)
        med = dt_median(res, 240)
        mode = 3 * med - 2 * mean
        factor = res / mode - 1
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def cal_customst(self):
        factor = self.st_factor()
        factor = arr_match_index(factor, self.cal_date_range, self.date_range)
        res = self.cal_groupst()
        return factor - res

    def result(self):
        return self.cal_customst()

if __name__=='__main__':
    val1 = cal_factor()


