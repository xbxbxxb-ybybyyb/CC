# coding: utf-8
# Author：fengchi863
# Date ：2021/12/24 14:40

from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.crossUtils import *
from basic.operators import *


class PSCorrStdAdj(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 30
    author = 'fc'
    freq = 'daily'
    logic = '全天均价与均价的标准差的相关性，除以其5日标准差，分组求均值'
    article = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': ['close_badj']}

    def st_factor(self):
        close = self.database['1min']['close_badj']
        twap = np.nanmean(close, axis=1, keepdims=True)
        twap_std = dt_std(twap, 10)
        corr = dt_corr2(twap, twap_std, 10)
        ret = corr / dt_std(corr, 5)
        return ret

    def calc_groupst(self):
        indicator = self.st_factor()
        group = sameshape(indicator, self.group_factor())
        group_ret = st2groupst(indicator, group, cross_mean)
        ret = arr_match_index(group_ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    # f = PSCorrStdAdj(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()