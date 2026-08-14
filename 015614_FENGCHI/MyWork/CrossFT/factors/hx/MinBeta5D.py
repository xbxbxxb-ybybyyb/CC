from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np


class MinBeta5D(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=5
    author='hx'
    logic='过去5交易日分钟Beta'
    article='兴业证券 (20160519):行业轮动系列专题报告. 基于不同市场情境下的行业轮动策略.'
    freq='1min'
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': ['ret_close', 'close_HS300']}

    def st_factor(self):
        ret = self.database['1min']['ret_close'] / 1000
        return ret

    def cal_groupst(self):
        self.factor = self.st_factor()
        self.stgroup = sameshape(self.factor, self.group_factor())
        calfunc = self.group_func()
        res = st2groupst(self.factor, self.stgroup, calfunc)

        ind_ret = index2st(self.database['1min']['close_HS300'], res.shape[-1])
        ind_ret = dt_pct(ind_ret, 1)
        beta = dt_beta2(res, ind_ret, 1210)
        return arr_match_index(beta, self.cal_date_range, self.date_range)

    def result(self):
        return self.cal_groupst()

if __name__=='__main__':
    f = MinBeta5D()
    #print(f.result())
    f.save_result()