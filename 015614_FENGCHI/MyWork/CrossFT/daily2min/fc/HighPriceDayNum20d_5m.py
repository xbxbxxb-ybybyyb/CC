# # coding: utf-8
# # Author：fengchi863
# # Date ：2021/8/23 11:02

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *


def ts_cumargmax_dis(x):
    arg = np.arange(x.shape[1])[:, None].astype('float32').repeat(x.shape[0] * x.shape[2], axis=1).reshape(
        x.shape[1], x.shape[0], x.shape[2]).transpose(1, 0, 2)
    arg[np.maximum.accumulate(x, axis=1) != x] = 0
    return (np.arange(x.shape[1]) + 1)[None, :, None].astype('float32') - np.maximum.accumulate(arg, axis=1)


class HighPriceDayNum20d_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 10
    author = 'fc'
    freq = '5mins'
    logic = '最高价距离现在的分钟数'
    article = '广发证券-20170330-多因子Alpha系列报告之三十'
    basic_datas = {'daily': [], '30mins': [], '5mins': ['close_badj']}

    def st_factor(self):
        close = self.database['5mins']['close_badj']
        high_num = ts_cumargmax_dis(close) * 5
        return high_num

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    # f = HighPriceDayNum20d_5m()
    # f.result()

    cal_factor()

