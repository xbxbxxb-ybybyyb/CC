# coding: utf-8
# Author：fengchi863
# Date ：2021/11/5 11:15

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class CVD1MIR(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 35
    author = 'fc'
    freq = 'daily'
    logic = '成交额变异系数-过去一个月的成交额标准差 / 成交额均值'
    article = '东北证券 20180307 – 《Replicating+Anomalies》A股检验'
    basic_datas = {'daily': ['amt'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        amt = self.database['daily']['amt']
        ret = dt_std(amt, 20) / dt_mean(amt, 20)
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
    # f = CVD1MIR()
    # print(f.result())

    cal_factor()
