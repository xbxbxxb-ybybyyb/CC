from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck
from basic.crossOperators import *

class ActiveOrderDoubleRank(crossFactor):
    cross_group='sw1'
    cross_func='cross_top10'
    extend_days=10
    author='hx'
    logic='个股主动挂单与行业因子值最大的10%股票平均挂单和'
    article=''
    freq='daily'
    basic_datas = {'5mins': ['turn_order_active_buy']}

    def st_factor(self):
        turn = self.database['5mins']['turn_order_active_buy']
        turn = np.nansum(turn, axis=1, keepdims=True)
        turn = dt_mean(turn, 10)
        return turn

    def cal_groupst(self):
        factor = self.st_factor()
        stgroup = sameshape(factor, self.group_factor())
        groups = np.unique(stgroup[np.isfinite(stgroup)])
        shape = factor.shape
        rank = np.full(factor.shape, np.nan)
        for g in groups:
            val = stgroup == g
            rank = np.where(val, bottleneck.nanrankdata(np.where(val, factor, np.nan), axis=len(shape) - 1), rank)
        count = st2groupst(rank, stgroup, cross_max)
        factor[rank / count <= 0.9] = np.nan
        factor = st2groupst(factor, stgroup, cross_mean)
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def cal_customst(self):
        factor = self.st_factor()
        factor = arr_match_index(factor, self.cal_date_range, self.date_range)
        res = self.cal_groupst()
        return factor + res

    def result(self):
        return self.cal_customst()

if __name__=='__main__':
    val1 = cal_factor()

