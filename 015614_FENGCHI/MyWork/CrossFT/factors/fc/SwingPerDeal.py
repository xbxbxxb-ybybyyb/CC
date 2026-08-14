# coding: utf-8
# Author：fengchi863
# Date ：2021/10/12 10:52

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class SwingPerDeal(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 15
    author = 'fc'
    freq = 'daily'
    logic = '振幅总和除以成交笔数，个股排序+行业排序'
    article = ''
    basic_datas = {'daily': ['volume'], '30mins': [], '5mins': [], '1min': ['high', 'low']}

    def st_factor(self):
        vol = self.database['daily']['volume']
        high = self.database['1min']['high']
        low = self.database['1min']['low']
        swing_sum = np.nansum((high - low) / low, axis=1, keepdims=True)
        return swing_sum / vol

    def cal_groupst(self):
        indicator = self.st_factor()
        group = sameshape(indicator, self.group_factor())
        groups = np.unique(group[np.isfinite(group)])
        res = np.full(indicator.shape[:-1] + (len(groups),), np.nan)
        for j, g in enumerate(groups):
            res[..., j] = self.group_func()(np.where(group == g, indicator, np.nan), axis=-1)
        res = bottleneck.nanrankdata(res, axis=-1) / np.sum(np.isfinite(res), axis=-1, keepdims=True)
        res2 = np.full(indicator.shape, np.nan)
        for j, g in enumerate(groups):
            res2 = np.where(group == g, res[..., [j]], res2)
        return arr_match_index(res2, self.cal_date_range, self.date_range)

    def cal_customst(self):
        indicator = self.st_factor()

        factor = bottleneck.nanrankdata(indicator, axis=-1) / np.sum(np.isfinite(indicator), axis=-1, keepdims=True)
        factor = arr_match_index(factor, self.cal_date_range, self.date_range)
        res = self.cal_groupst()
        return factor + res

    def result(self):
        return self.cal_customst()


if __name__ == '__main__':
    # f = IlliqShortcut(start=20210401, end=20210501)
    # print(f.result())

    val = cal_factor('/data/user/015614/MyWork/CrossFT/factors/fc', 'SwingPerDeal.py', {'daily': 6}, notrun=False)
