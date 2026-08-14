# coding: utf-8
# Author：fengchi863
# Date ：2021/8/23 11:25

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *


class UpDownAmtRatio26d(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 40
    author = 'fc'
    freq = 'daily'
    logic = '前26日内上涨的成交量/下降的成交量'
    article = '广发证券-20170330-多因子Alpha系列报告之三十'
    basic_datas = {'daily': ['pct_chg', 'volume']}

    def st_factor(self):
        pctchg = self.database['daily']['pct_chg']
        vol = self.database['daily']['volume']
        pctchg = pctchg > 0
        pctchg = 2 * pctchg - 1
        ret = vol * pctchg
        ret_up = ret.copy()
        ret_down = ret.copy()
        ret_up[ret < 0] = np.nan
        ret_down[ret > 0] = np.nan
        ret2 = dt_mean(ret_up, 26)
        # ret2 = ret_up / ret_down
        # ret2 =
        # ret2[ret2 != ret2] = 0
        return np.where(np.isfinite(ret2), ret2, 0)

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    # f = UpDownAmtRatio26d()
    # print(f.result())

    val1 = cal_factor(numd={})
    val2 = cal_factor(numd={'daily': 10})
    gap = abs(val1 - val2)
    print(np.nansum(gap))
