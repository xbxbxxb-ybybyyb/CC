# coding: utf-8
# Author：fengchi863
# Date ：2021/10/27 13:22

from xquant.factordata import FactorData

from ShortTermTrading.dataApi import stockList
from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.crossUtils import *


class HolderPctIR(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 0
    author = 'fc'
    freq = 'daily'
    logic = '个股的股东持仓比例 个股排名 + 分组排名' # 表征行业特征
    article = '东方证券 20200901 – 因子选股系列研究之六十九'
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        fd = FactorData()
        check = get_quarter_1factor('holder_pct', code_list=self.code_list)
        holder_pct = fd.get_factor_value('Basic_factor',
                                         stock=list(map(str, self.code_list)),
                                         mddate=list(map(str, self.cal_date_range)),
                                         factor_names=['holder_pct'])
        holder_pct2 = holder_pct.reset_index()
        holder_pct3 = holder_pct2.pivot(index='mddate', columns='stock', values='holder_pct')
        holder_pct3.index = holder_pct3.index.map(int)
        holder_pct3.columns = holder_pct3.columns.map(stockList.trans_windcode2int)
        holder_pct3 = holder_pct3.loc[self.cal_date_range, self.code_list]
        return holder_pct3.values

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
    f = HolderPctIR()
    print(f.result())

    cal_factor()
