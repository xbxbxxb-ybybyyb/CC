# coding: utf-8
# Author：fengchi863
# Date ：2021/10/27 13:22

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *
from xquant.factordata import FactorData
import sys
sys.path.append('/data/group/800442/800319')
from dataApi import stockList


class ReportNumIR(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 0
    author = 'fc'
    freq = 'daily'
    logic = '个股的周报告数比例 个股排名 + 分组排名'
    article = '东方证券 20200901 – 因子选股系列研究之六十九'
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        fd = FactorData()
        report_number = fd.get_factor_value('Basic_factor',
                                     stock=list(map(str, self.code_list)),
                                     mddate=list(map(str, self.cal_date_range)),
                                     factor_names=['report_number7'])
        report_number2 = report_number.reset_index()
        report_number3 = report_number2.pivot(index='mddate', columns='stock', values='report_number7')
        report_number3.index = report_number3.index.map(int)
        report_number3.columns = report_number3.columns.map(stockList.trans_windcode2int)
        report_number3 = report_number3.loc[self.cal_date_range, self.code_list]
        return report_number3.values

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
    # f = ReportNumIR()
    # print(f.result())

    cal_factor()
