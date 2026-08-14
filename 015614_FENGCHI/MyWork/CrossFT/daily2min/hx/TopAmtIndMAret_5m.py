from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class TopAmtIndMAret_5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=20
    author='hx'
    logic='过去10日换手率最大的Top5股票相对20日均线收益率+个股相对20日均线收益率'
    article=''
    freq='5mins'
    basic_datas = {'5mins': ['turn_total', 'close_badj']}

    def st_factor(self):
        factor = self.database['5mins']['close_badj']
        MA20 = dt_mean(factor, 20)
        factor = factor / MA20 - 1
        return factor

    def cal_groupst(self):
        factor = self.st_factor()
        turn = self.database['5mins']['turn_total']
        turn = dt_mean(turn, 10)
        stgroup = sameshape(turn, self.group_factor())
        groups = np.unique(stgroup[np.isfinite(stgroup)])
        shape = turn.shape
        rank = np.full(turn.shape, np.nan)
        for g in groups:
            val = stgroup == g
            rank = np.where(val, bottleneck.nanrankdata(np.where(val, -turn, np.nan), axis=len(shape) - 1), rank)
        factor[rank > 5] = np.nan
        res = st2groupst(factor, stgroup, self.group_func())
        return res

    def cal_customst(self):
        factor = self.st_factor() + self.cal_groupst()
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        return self.cal_customst()


if __name__ == '__main__':
    val1 = cal_factor(start=20210101, end=20210630)
