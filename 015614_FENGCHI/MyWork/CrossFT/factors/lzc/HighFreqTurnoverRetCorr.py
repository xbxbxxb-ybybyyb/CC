# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File :HighFreqTurnoverRetCorr.py

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class HighFreqTurnoverRetCorr(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 0
    author = 'lzc'
    logic = '日内换手率和收益的相关性 * 分组面板相关性'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['free_float_shares', 'close'], '30mins': [], '5mins': ['close', 'amt'], '1min': []}

    window = 15

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return [self.database['5mins'][x] for x in ['close', 'amt']]

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        close, amt = self.st_factor()
        self.group = sameshape(self.database['daily']['free_float_shares'], self.group_factor())
        free_float_cap = self.database['daily']['free_float_shares'] * self.database['daily']['close']

        ret = (close.swapaxes(0, 1) / delay(close.swapaxes(0, 1), 1)).swapaxes(0, 1)
        X = amt / free_float_cap

        count_X = np.isfinite(X)
        count_y = np.isfinite(ret)
        count = count_X & count_y

        X = np.where(count, X, 0)
        y = np.where(count, ret, 0)

        X2 = X ** 2
        y2 = y ** 2
        Xy = X * y

        SUM_X = np.sum(X, axis=1)[:, None, :]
        SUM_Y = np.sum(y, axis=1)[:, None, :]
        SUM_XY = np.sum(Xy, axis=1)[:, None, :]
        SUM_X2 = np.sum(X2, axis=1)[:, None, :]
        SUM_Y2 = np.sum(y2, axis=1)[:, None, :]
        SUM_COUNT = np.sum(count, axis=1)[:, None, :]
        stk_corr = (SUM_COUNT * SUM_XY - SUM_X * SUM_Y) / ((SUM_COUNT * SUM_X2 - SUM_X ** 2) ** 0.5) / ((SUM_COUNT * SUM_Y2 - SUM_Y ** 2) ** 0.5)
        SUM_X, SUM_Y, SUM_XY, SUM_X2, SUM_Y2, SUM_COUNT = [st2groupst(x, self.group, cross_sum) for x in [SUM_X, SUM_Y, SUM_XY, SUM_X2, SUM_Y2, SUM_COUNT]]
        group_corr = (SUM_COUNT * SUM_XY - SUM_X * SUM_Y) / ((SUM_COUNT * SUM_X2 - SUM_X ** 2) ** 0.5) / ((SUM_COUNT * SUM_Y2 - SUM_Y ** 2) ** 0.5)

        return arr_match_index(stk_corr + group_corr, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    # f = RelativePriceAbsRetCorr()
    # f.result()
    cal_factor(numd={})
