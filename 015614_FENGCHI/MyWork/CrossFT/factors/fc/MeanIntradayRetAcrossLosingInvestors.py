# coding: utf-8
# Author：fengchi863
# Date ：2021/11/16 11:11

from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.crossUtils import *
from basic.operators import *


class MeanIntradayRetAcrossLosingInvestors(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 2
    author = 'fc'
    freq = 'daily'
    logic = '每日分钟线路径上到收盘的收益，按成交额为权重计算所有浮盈的收益率'
    article = ''
    basic_datas = {'daily': ['close_badj'], '30mins': [], '5mins': [], '1min': ['close_badj', 'amt']}

    def st_factor(self):
        close = self.database['1min']['close_badj']
        daily_close = self.database['daily']['close_badj']
        pct = close / daily_close
        amt = self.database['1min']['amt']
        return pct, amt

    def calc_groupst(self):
        pct, amt = self.st_factor()
        amt_weight = amt / np.nanmean(amt, axis=1, keepdims=True)
        pct_0 = np.where(pct < 0, pct, 0)
        ret_0 = np.nansum(pct_0 * amt_weight, axis=1, keepdims=True)
        group = sameshape(ret_0, self.group_factor())
        group_ret = st2groupst(ret_0, group, self.group_func())
        ret = arr_match_index(group_ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    # f = MeanIntradayRetAcrossGainingInvestors(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()
