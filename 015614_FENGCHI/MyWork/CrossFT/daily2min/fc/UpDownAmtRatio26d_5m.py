# coding: utf-8
# Author：fengchi863
# Date ：2021/8/23 11:25

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *


class UpDownAmtRatio26d_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 40
    author = 'fc'
    freq = '5mins'
    logic = '前2个小时内上涨的成交量/下降的成交量'
    article = '广发证券-20170330-多因子Alpha系列报告之三十'
    basic_datas = {'5mins': ['close_badj', 'volume']}

    def st_factor(self):
        close = self.database['5mins']['close_badj']
        pctchg = dt_pct(close, 1)
        vol = self.database['5mins']['volume']
        pctchg = pctchg > 0
        pctchg = 2 * pctchg - 1
        ret = vol * pctchg
        ret_up = ret.copy()
        ret_down = ret.copy()
        ret_up[ret < 0] = np.nan
        ret_down[ret > 0] = np.nan
        ret2 = dt_mean(ret_up, 24)
        # ret2 = ret_up / ret_down
        # ret2 =
        # ret2[ret2 != ret2] = 0
        return np.where(np.isfinite(ret2), ret2, 0)

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    # f = UpDownAmtRatio26d_5m()
    # print(f.result())

    cal_factor()
