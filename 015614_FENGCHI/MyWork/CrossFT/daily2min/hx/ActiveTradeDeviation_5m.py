from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
from basic.crossOperators import *


class ActiveTradeDeviation_5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_dev'
    extend_days=10
    author='hx'
    logic='个股10日主动买入换手率与其行业离差之比'
    article=''
    freq='5mins'
    basic_datas = {'5mins': ['turn_trade_buy']}

    def st_factor(self):
        turn = self.database['5mins']['turn_trade_buy']
        # turn = np.nansum(turn, axis=1, keepdims=True)
        turn = dt_mean(turn, 24)
        return turn

    def cal_groupst(self):
        factor = self.st_factor()
        stgroup = sameshape(factor, self.group_factor())
        plus = st2groupst(factor, stgroup, cross_sum)
        mad = st2groupst(factor, stgroup, cross_median)
        lms = pn_condition2(factor - mad, factor)
        lms = st2groupst(lms, stgroup, cross_sum)
        lms /= plus
        return arr_match_index(lms, self.cal_date_range, self.date_range)

    def cal_customst(self):
        factor = self.st_factor()
        factor = arr_match_index(factor, self.cal_date_range, self.date_range)
        res = self.cal_groupst()
        return factor / res

    def result(self):
        return self.cal_customst()

if __name__=='__main__':
    # f = ActiveTradeDeviation()
    #print(f.result())
    # f.save_result()
    val1 = cal_factor(start=20210101, end=20210630)
