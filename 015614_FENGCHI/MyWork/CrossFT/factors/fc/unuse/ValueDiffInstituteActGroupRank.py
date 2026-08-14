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


class ValueDiffInstituteActGroupRank(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 0
    author = 'fc'
    freq = 'daily'
    logic = '分组特大单（机构）主动买额-分组特大单（机构）主动卖额 分组排名'
    article = '安信证券 20200624 – 北向资金交易能力一定强吗'
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        fd = FactorData()
        value_diff_institute_act = fd.get_factor_value('Basic_factor',
                                         stock=self.code_list,
                                         mddate=list(map(str, self.cal_date_range)),
                                         factor_names=['value_diff_institute_act'])
        value_diff_institute_act2 = value_diff_institute_act.reset_index()
        value_diff_institute_act3 = value_diff_institute_act2.pivot(index='mddate', columns='stock', values='value_diff_institute_act')
        value_diff_institute_act3.index = value_diff_institute_act3.index.map(int)
        value_diff_institute_act3.columns = value_diff_institute_act3.columns.map(stockList.trans_windcode2int)
        value_diff_institute_act3 = value_diff_institute_act3.loc[self.cal_date_range, self.code_list]
        return value_diff_institute_act3.values

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
    # f = ValueDiffInstituteActGroupRank()
    # print(f.result())

    cal_factor()
