# coding: utf-8
# Author：fengchi863
# Date ：2021/11/8 14:12

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


class PriceAmtRelYesRatioCorrGroupMean(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 5
    author = 'fc'
    freq = '1min'
    logic = '分钟成交量和分钟均价，与上个交易日同时段分钟成交量和分钟均价之比的Spearman相关系数，组内求平均'
    article = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': ['amt', 'close_badj']}

    def st_factor(self):
        amt = self.database['1min']['amt']
        close = self.database['1min']['close_badj']

        amt_ratio = amt / _fill(amt[:-1, :, :], 1, axis=0)
        close_ratio = close / _fill(close[:-1, :, :], 1, axis=0)

        corr = ts_cumcorr2(close_ratio, amt_ratio)
        return corr

    def calc_groupst(self):
        ret = self.st_factor()
        group = sameshape(ret, self.group_factor())
        ret = st2groupst(ret, group, cross_mean)
        factor = arr_match_index(ret, self.cal_date_range, self.date_range)
        return factor

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    # f = PriceAmtRelYesRatioCorrGroupMean()
    # print(f.result())

    cal_factor()
