# coding: utf-8
# Author：fengchi863
# Date ：2021/11/4 10:32

from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.crossUtils import *
from basic.operators import *


class HighLowDiffVwapCorrIR(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 35
    author = 'fc'
    freq = 'daily'
    logic = '最高价与最低价的差，与当日均价的相关系数，个股排序 + 行业排序'
    article = ''
    basic_datas = {'daily': ['high_badj', 'low_badj', 'vwap'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        high = self.database['daily']['high_badj']
        low = self.database['daily']['low_badj']
        vwap = self.database['daily']['vwap']
        corr = dt_corr2(high - low, vwap, 30)
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
    # f = HighLowDiffVwapCorrIR()
    # print(f.result())

    cal_factor()
