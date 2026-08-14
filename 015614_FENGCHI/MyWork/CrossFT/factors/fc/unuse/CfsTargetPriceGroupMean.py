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


class CfsTargetPriceGroupMean(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 0
    author = 'fc'
    freq = 'daily'
    logic = '组内一致预期与价格的距离 求分组均值'
    article = '东方证券 20200901 – 因子选股系列研究之六十九'
    basic_datas = {'daily': ['close'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        fd = FactorData()
        cfs_target_price = fd.get_factor_value('Basic_factor',
                                         stock=list(map(str, self.code_list)),
                                         mddate=list(map(str, self.cal_date_range)),
                                         factor_names=['cfs_target_price'])
        cfs_target_price2 = cfs_target_price.reset_index()
        cfs_target_price3 = cfs_target_price2.pivot(index='mddate', columns='stock', values='cfs_target_price')
        cfs_target_price3.index = cfs_target_price3.index.map(int)
        cfs_target_price3.columns = cfs_target_price3.columns.map(stockList.trans_windcode2int)
        cfs_target_price3 = cfs_target_price3.loc[self.cal_date_range, self.code_list].values

        close = self.database['daily']['close']
        dis = cfs_target_price3 / close[:, 0, :] - 1

        return dis

    def calc_groupst(self):
        indicator = self.st_factor()

        group = sameshape(indicator, self.group_factor())
        group_ret = st2groupst(indicator, group, cross_mean)
        ret = arr_match_index(group_ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    # f = CfsTargetPriceGroupMean(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()
