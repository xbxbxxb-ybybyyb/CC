# coding: utf-8
# Author：fengchi863
# Date ：2021/11/12 13:30

from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.crossUtils import *
from basic.operators import *


class MinVolBurstRetSumGroupMean(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 2
    author = 'fc'
    freq = 'daily'
    logic = 'Volume比10分钟均线高三倍的时候的和的PCTCHG求平均'
    article = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': ['close_badj', 'volume']}

    def st_factor(self):
        close = self.database['1min']['close_badj']
        vol = self.database['1min']['volume']
        vol_mean = dt_mean(vol, 10)
        vol_mean[:, :10, :] = np.nan
        flag = vol > vol_mean
        pctchg = dt_pct(close, 1)
        pctchg_vol_up = np.where(flag, pctchg, 0)
        ret = np.nanmean(pctchg_vol_up, axis=1, keepdims=True)
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
    # f = MinVolBurstRetSumGroupMean(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()