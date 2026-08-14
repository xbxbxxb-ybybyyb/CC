# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File :SwingCorrWithPriceSeriesSharpe.py

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class SwingCorrWithPriceSeriesSharpe(crossFactor):
    cross_group = 'sw1'
    cross_func = ''
    extend_days = 0
    author = 'lzc'
    logic = '分钟K涨跌幅 与 价格相关性 截面sharpe'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['free_float_shares'], '30mins': [], '5mins': ['close', 'high', 'low'], '1min': []}

    window = 15

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return [self.database['5mins'][x] for x in ['close', 'high', 'low']]

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        close, high, low = self.st_factor()

        daily = sameshape(self.database['daily']['free_float_shares'], self.group_factor())
        netlize_close = close / close[:, [0], :]
        swing = high / low - 1
        count = np.isfinite(swing) & np.isfinite(netlize_close)
        X = np.where(count, swing, 0)
        Y = np.where(count, netlize_close, 0)

        SUMX2 = np.nansum(X ** 2, axis=1)[:, None, :]
        SUMY2 = np.nansum(Y ** 2, axis=1)[:, None, :]
        SUMXY = np.nansum(X * Y, axis=1)[:, None, :]
        SUMY = np.nansum(Y, axis=1)[:, None, :]
        SUMX = np.nansum(X, axis=1)[:, None, :]
        COUNT = np.nansum(count, axis=1)[:, None, :]

        stk_corr = (COUNT * SUMXY - SUMY * SUMX) / (COUNT * SUMX2 - SUMX ** 2) ** 0.5 / (COUNT * SUMY2 - SUMY ** 2) ** 0.5

        factor = (stk_corr - st2groupst(stk_corr, daily, cross_mean)) / st2groupst(stk_corr, daily, cross_std)

        return arr_match_index(factor, self.cal_date_range, self.date_range)

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
