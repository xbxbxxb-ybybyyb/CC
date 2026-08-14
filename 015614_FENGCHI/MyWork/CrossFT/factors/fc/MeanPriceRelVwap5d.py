# coding: utf-8
# Author：fengchi863
# Date ：2021/12/23 19:31

from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.crossUtils import *
from basic.operators import *


class MeanPriceRelVwap5d(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 6
    author = 'fc'
    freq = 'daily'
    logic = '全天均价与vwap的比值取五日平均，分组求平均'
    article = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': ['close_badj', 'amt', 'volume']}

    def st_factor(self):
        close = self.database['1min']['close_badj']
        amt = self.database['1min']['amt']
        vol = self.database['1min']['volume']
        twap = np.nanmean(close, axis=1, keepdims=True)
        vwap = np.nansum(amt, axis=1, keepdims=True) / np.nanmean(vol, axis=1, keepdims=True)
        ret = twap / vwap
        return ret

    def calc_groupst(self):
        indicator = self.st_factor()
        group = sameshape(indicator, self.group_factor())
        group_ret = st2groupst(indicator, group, cross_mean)
        ret = arr_match_index(group_ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    # f = MeanPriceRelVwap5d(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()
