# coding: utf-8
# Author：fengchi863
# Date ：2021/11/16 13:23

from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.crossUtils import *
from basic.operators import *


class SwingVwapCorrBias5d(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 30
    author = 'fc'
    freq = 'daily'
    logic = '振幅与均价的相关性，5日偏离度，个股排序+行业排序'
    article = ''
    basic_datas = {'daily': ['vwap', 'swing'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        close = self.database['daily']['vwap']
        swing = self.database['daily']['swing']
        corr = dt_corr2(close, swing, 10)
        ret = dt_skew(corr, 5)
        return ret

    def calc_groupst(self):
        indicator = self.st_factor()

        group = sameshape(indicator, self.group_factor())
        groups = np.unique(group[np.isfinite(group)])
        res = np.full(indicator.shape[:-1] + (len(groups),), np.nan)
        for j, g in enumerate(groups):
            res[..., j] = self.group_func()(np.where(group == g, indicator, np.nan), axis=-1)
        res = res / np.nansum(res, axis=-1, keepdims=True)
        res2 = np.full(indicator.shape, np.nan)
        for j, g in enumerate(groups):
            res2 = np.where(group == g, res[..., [j]], res2)
        return arr_match_index(res2, self.cal_date_range, self.date_range)

    def result(self):
        indicator = self.st_factor()
        group = sameshape(indicator, self.group_factor())
        group_sum = st2groupst(indicator, group, cross_sum)
        indicator = indicator / group_sum
        indicator = arr_match_index(indicator, self.cal_date_range, self.date_range)
        res = self.cal_groupst()
        return indicator + res


if __name__ == '__main__':
    # f = HighCloseDistanceGroupMean(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()