# coding: utf-8
# Author：fengchi863
# Date ：2021/10/27 13:22

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *
from xquant.factordata import FactorData
from FaaMonitor.dataApi import stockList


class GroupNetInflow(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 0
    author = 'fc'
    freq = 'daily'
    logic = '板块的资金净流入额排名'
    article = '安信证券 20200624 – 北向资金交易能力一定强吗'
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        fd = FactorData()
        mfd_inflow = fd.get_factor_value('Basic_factor',
                                         stock=self.code_list,
                                         mddate=list(map(str, self.cal_date_range)),
                                         factor_names=['mfd_inflow'])
        mfd_inflow2 = mfd_inflow.reset_index()
        mfd_inflow3 = mfd_inflow2.pivot(index='mddate', columns='stock', values='mfd_inflow')
        mfd_inflow3.index = mfd_inflow3.index.map(int)
        mfd_inflow3.columns = mfd_inflow3.columns.map(stockList.trans_windcode2int)
        mfd_inflow3 = mfd_inflow3.loc[self.cal_date_range, self.code_list]
        return mfd_inflow3.values

    def calc_groupst(self):
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

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    # f = GroupNetInflow()
    # print(f.result())

    cal_factor()
