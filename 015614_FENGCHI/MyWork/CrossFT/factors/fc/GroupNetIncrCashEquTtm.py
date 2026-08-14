# coding: utf-8
# Author：fengchi863
# Date ：2021/8/31 9:52

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class GroupNetIncrCashEquTtm(crossFactor):
    cross_group = 'citics1'
    cross_func = 'cross_mean'
    extend_days = 0
    author = 'fc'
    freq = 'daily'
    logic = '个股现金及现金等价物净额增加额按市值加权'
    article = '光大证券 20200423 – 多因子系列报告之三十二'
    basic_datas = {'daily': ['net_incr_cash_cash_equ_ttm', 'a_mkt_cap'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        net_incr = self.database['daily']['net_incr_cash_cash_equ_ttm']
        cap = self.database['daily']['a_mkt_cap']
        return net_incr, cap

    def calc_groupst(self):
        net_incr, cap = self.st_factor()
        tmp_ret = net_incr / cap
        self.group = sameshape(tmp_ret, self.group_factor())
        group_ret = st2groupst(tmp_ret, self.group, cross_mean)
        ret = arr_match_index(group_ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    f = GroupNetIncrCashEquTtm()
    val1 = f.result().astype('float32')
    val2 = cal_factor('data/user/016385/test/crossft/factors/fc', '1.py', {'daily': 6}, notrun=False)
    print(np.nansum(abs(val1 - val2)))
