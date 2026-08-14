# coding: utf-8
# Author：fengchi863
# Date ：2021/12/17 9:52

from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.crossUtils import *
from basic.operators import *


class RetVolCorr_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 2
    author = 'fc'
    freq = '5mins'
    logic = '与上个交易日同时段的成交量和收益的相关性'
    article = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': ['close_badj', 'volume']}

    def st_factor(self):
        close = self.database['1min']['close_badj']
        pct = dt_pct(close, 1)
        vol = self.database['1min']['volume']
        corr = ds_corr2(pct, vol, 8)
        return cross_resample(corr, '5mins')

    def calc_groupst(self):
        indicator = self.st_factor()
        group = sameshape(indicator, self.group_factor())
        group_ret = st2groupst(indicator, group, cross_mean)
        ret = arr_match_index(group_ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    # f = RetVolCorr_5m(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()