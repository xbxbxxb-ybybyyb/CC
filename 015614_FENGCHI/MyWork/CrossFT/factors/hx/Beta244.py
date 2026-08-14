from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np


class Beta244(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=245
    author='hx'
    logic='过去244交易日Beta'
    article='兴业证券 (20160519):行业轮动系列专题报告. 基于不同市场情境下的行业轮动策略.'
    freq='daily'
    basic_datas = {'daily': ['pct_chg', 'close_HS300'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        ret = self.database['daily']['pct_chg'] / 100
        return ret

    def cal_groupst(self):
        self.factor = self.st_factor()
        self.stgroup = sameshape(self.factor, self.group_factor())
        calfunc = self.group_func()
        res = st2groupst(self.factor, self.stgroup, calfunc)

        ind_ret = index2st(self.database['daily']['close_HS300'], res.shape[-1])
        ind_ret = dt_pct(ind_ret, 1)
        beta = dt_beta2(res, ind_ret, 244)
        return arr_match_index(beta, self.cal_date_range, self.date_range)

    def result(self):
        return self.cal_groupst()

if __name__=='__main__':
    f = Beta244()
    #print(f.result())
    f.save_result()