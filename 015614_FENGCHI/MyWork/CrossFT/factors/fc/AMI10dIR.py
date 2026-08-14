# coding: utf-8
# Author：fengchi863
# Date ：2021/11/5 10:44

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class AMI10dIR(crossFactor):
    cross_group = 'sw2'
    cross_func = 'cross_mean'
    extend_days = 10
    start = 20140701
    # start = 20210525
    end = 20210531
    author = 'fc'
    freq = 'daily'
    logic = '流动性因子-收益率绝对值均值/成交额均值'
    article = '东北证券 20180307 – 《Replicating+Anomalies》A股检验'
    basic_datas = {'daily': ['pct_chg', 'amt'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        amt = self.database['daily']['amt']
        pctchg = self.database['daily']['pct_chg']
        ret = dt_mean(abs(pctchg), 5) / dt_mean(amt, 5)
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
    # f = AMI10dIR()
    # print(f.result())

    cal_factor()
