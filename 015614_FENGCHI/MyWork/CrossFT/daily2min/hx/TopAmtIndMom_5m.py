from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class TopAmtIndMom_5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=10
    author='hx'
    logic='换手率最大的Top5股票动量+个股动量'
    article=''
    freq='5mins'
    basic_datas = {'5mins': ['turn_total', 'ret_close']}

    def st_factor(self):
        factor = self.database['5mins']['ret_close']
        return factor

    def cal_groupst(self):
        ret = self.database['5mins']['ret_close']
        turn = self.database['5mins']['turn_total']
        stgroup = sameshape(turn, self.group_factor())
        groups = np.unique(stgroup[np.isfinite(stgroup)])
        shape = turn.shape
        rank = np.full(turn.shape, np.nan)
        for g in groups:
            val = stgroup == g
            rank = np.where(val, bottleneck.nanrankdata(np.where(val, -turn, np.nan), axis=len(shape) - 1), rank)
        ret[rank > 5] = np.nan
        res = st2groupst(ret, stgroup, self.group_func())
        return res

    def cal_customst(self):
        factor = self.st_factor() + self.cal_groupst()
        factor = dt_mean(factor, 10)
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        return self.cal_customst()


if __name__ == '__main__':
    val1 = cal_factor(start=20210101, end=20210630)
