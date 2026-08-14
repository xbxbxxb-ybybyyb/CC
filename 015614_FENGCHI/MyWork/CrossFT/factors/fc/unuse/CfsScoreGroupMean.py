# coding: utf-8
# Author：fengchi863
# Date ：2021/11/1 10:47

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *
from xquant.factordata import FactorData
import sys
sys.path.append('/data/group/800442/800319')
from dataApi import stockList

from xquant.factordata import FactorData
from xquant.marketdata import MarketData
from xquant.thirdpartydata.multifactor.IO import *
from xquant.futuredata import FutureData
class CfsScoreGroupMean(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 0
    author = 'fc'
    freq = 'daily'
    logic = '组内个股的一致预期评级 均值'
    article = '东方证券 20200901 – 因子选股系列研究之六十九'
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        fd = FactorData()
        cfs_score = fd.get_factor_value('Basic_factor',
                                         stock=list(map(str, self.code_list)),
                                         mddate=list(map(str, self.cal_date_range)),
                                         factor_names=['cfs_score'])
        cfs_score2 = cfs_score.reset_index()
        cfs_score3 = cfs_score2.pivot(index='mddate', columns='stock', values='cfs_score')
        cfs_score3.index = cfs_score3.index.map(int)
        cfs_score3.columns = cfs_score3.columns.map(stockList.trans_windcode2int)
        cfs_score3 = cfs_score3.loc[self.cal_date_range, self.code_list].values  # 应该是越小越好

        return cfs_score3

    def calc_groupst(self):
        indicator = self.st_factor()

        group = sameshape(indicator, self.group_factor())
        group_ret = st2groupst(indicator, group, cross_mean)
        ret = arr_match_index(group_ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    # f = CfsScoreGroupMean(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()
