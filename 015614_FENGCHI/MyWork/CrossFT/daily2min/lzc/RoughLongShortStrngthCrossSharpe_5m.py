# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : RoughLongShortStrngthCrossSharpe.py

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class RoughLongShortStrngthCrossSharpe_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 32
    author = 'lzc'
    logic = '近似多空力量截面sharpe'
    article = ''
    freq = '5mins'
    basic_datas = {'daily': [], '30mins': [], '5mins': ['free_float_shares', 'close', 'high', 'low', 'amt'], '1min': []}

    window = 15

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return [self.database['5mins'][x] for x in ['free_float_shares', 'close', 'high', 'low', 'amt']]

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        free_float_shares, close, high, low, amt = self.st_factor()
        minute_group = sameshape(free_float_shares, self.group_factor())
        Turnover = amt / close / free_float_shares
        factor = (2 * close / (high + low) - 1) * Turnover
        factor = st2groupst(factor, minute_group, cross_mean) / st2groupst(factor, minute_group, cross_std)
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    # f = RoughLongShortStrngthCrossSharpe()
    # f.result()
    cal_factor(numd={})
