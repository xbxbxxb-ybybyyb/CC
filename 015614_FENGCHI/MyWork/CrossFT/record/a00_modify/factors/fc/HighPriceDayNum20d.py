# # coding: utf-8
# # Author：fengchi863
# # Date ：2021/8/23 11:02

from basic.crossFactor import crossFactor
from basic.crossUtils import *


class HighPriceDayNum20d(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=30
    author='fc'
    freq='daily'
    logic='前20日内最高价距离现在的天数'
    article='广发证券-20170330-多因子Alpha系列报告之三十'


    def st_factor(self):
        N = 20
        ret = get_daily_1factor('close_badj', self.cal_date_range, self.code_list)
        high_num = ret.rolling(N).apply(lambda x: N - np.argmax(x))
        return high_num

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    f = HighPriceDayNum20d()
    f.save_result()