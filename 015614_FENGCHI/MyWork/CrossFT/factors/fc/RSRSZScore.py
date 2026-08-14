# coding: utf-8
# Author：fengchi863
# Date ：2021/11/11 11:18

from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.crossUtils import *
from basic.operators import *


class RSRSZScore(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 30
    author = 'fc'
    freq = 'daily'
    logic = '相对阻力支撑强度指标，High相对Low回归得到的beta, 个股组内STD'
    article = ''
    basic_datas = {'daily': ['high_badj', 'low_badj'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        low = self.database['daily']['low_badj']
        high = self.database['daily']['high_badj']
        ret = dt_beta2(high, low, 8)
        return ret

    def cal_groupst(self):
        indicator = self.st_factor()
        group = sameshape(indicator, self.group_factor())
        indicator_std = dt_std(indicator, 8)
        indicator_std_zscore = (indicator_std - st2groupst(indicator_std, group, cross_mean)) / st2groupst(indicator_std, group, cross_std)

        return arr_match_index(indicator_std_zscore, self.cal_date_range, self.date_range)

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    # f = RSRSZScore(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()
