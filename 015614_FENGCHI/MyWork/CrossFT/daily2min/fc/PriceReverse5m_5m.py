# coding: utf-8
# Author：fengchi863
# Date ：2021/8/23 10:23
'''
反转类因子
'''

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import ds_pct


class PriceReverse5m_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 5
    author = 'fc'
    freq = '5mins'
    logic = '五分钟股价反转'
    article = '广发证券-20170330-多因子Alpha系列报告之三十'
    basic_datas = {'5mins': ['close_badj']}

    def st_factor(self):
        ret = ds_pct(self.database['5mins']['close_badj'], 1)
        ret[:, 0, :] = np.nan
        return ret

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    cal_factor()