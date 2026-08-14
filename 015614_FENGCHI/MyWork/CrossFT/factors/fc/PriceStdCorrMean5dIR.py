# coding: utf-8
# Author：fengchi863
# Date ：2021/11/4 10:41

from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.crossUtils import *
from basic.operators import *


class PriceStdCorrMean5dIR(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 35
    author = 'fc'
    freq = 'daily'
    logic = '日内均值与日内均值的标准差的相关系数，个股排序 + 行业排序'
    article = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': ['close_badj', 'amt']}

    def st_factor(self):
        close = self.database['1min']['close_badj']
        amt = self.database['1min']['amt']
        vwap = np.nansum(close * amt, axis=1, keepdims=True) / np.nansum(amt, axis=1, keepdims=True)
        std = np.nanstd(close, axis=1, keepdims=True)
        corr = dt_corr2(vwap, std, 30)
        return corr

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
    f = PriceStdCorrMean5dIR(start=20210401, end=20210501)
    print(f.result())

    cal_factor()
