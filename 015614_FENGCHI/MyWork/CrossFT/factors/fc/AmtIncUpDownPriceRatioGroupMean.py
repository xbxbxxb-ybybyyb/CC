# coding: utf-8
# Author：fengchi863
# Date ：2021/11/9 14:11

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


def _fill(arr, l, axis=0):
    if arr.ndim == 2:
        return np.pad(arr, ((l, 0), (0, 0)), mode='constant', constant_values=np.nan)

    elif arr.ndim == 3:
        if axis:
            return np.pad(arr, ((0, 0), (l, 0), (0, 0)), mode='constant', constant_values=np.nan)
        else:
            return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)

    else:
        raise ValueError


class AmtIncUpDownPriceRatioGroupMean(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 5
    author = 'fc'
    freq = 'daily'
    logic = '分钟成交量高于上一分钟的时间段内，平均升高价格和平均降低价格之比'
    article = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': ['amt', 'close_badj']}

    def st_factor(self):
        amt = self.database['1min']['amt']
        close = self.database['1min']['close_badj']

        amt_flag = amt > ds_delay(amt, 1)
        pct = ds_pct(close, 1)
        pct = np.where(amt_flag, pct, np.nan)

        pct1 = np.where(pct > 0, pct, np.nan)
        pct2 = np.where(pct < 0, pct, np.nan)

        ratio = np.divide(np.nanmean(pct1, axis=1), np.nanmean(pct2, axis=1),
                          where=abs(np.nanmean(pct2, axis=1)) > 1e-8)
        return ratio

    def calc_groupst(self):
        ret = self.st_factor()
        group = sameshape(ret, self.group_factor())
        ret = st2groupst(ret, group, cross_mean)
        factor = arr_match_index(ret, self.cal_date_range, self.date_range)
        return factor

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    # f = AmtIncUpDownPriceRatioGroupMean(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()
