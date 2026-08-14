# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File :IntradayTurnoverStd.py

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class IntradayTurnoverStd(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 32
    author = 'lzc'
    logic = '日内分钟K换手率波动率近30日sharpe'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['free_float_shares', 'close'], '30mins': [], '5mins': ['amt'], '1min': []}

    window = 15

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return [self.database['5mins'][x] for x in ['amt']] + [self.database['daily'][x] for x in ['free_float_shares', 'close']]

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        amt, free_float_shares, close = self.st_factor()
        daily_group = sameshape(free_float_shares, self.group_factor())
        turover = amt / delay(free_float_shares, 1) / delay(close, 1)
        intraday_std = np.nanstd(turover, axis=1)[:, None, :]
        intraday_std_30 = [intraday_std]
        for i in range(1, 30):
            intraday_std_30.append(delay(intraday_std, 1))
        intraday_std_30 = np.concatenate(tuple(intraday_std_30), axis=1)  # [:,None,:]
        shapre = np.nanmean(intraday_std_30, axis=1) / np.nanstd(intraday_std_30, axis=1)
        shapre = shapre[:, None, :]
        factor = shapre * st2groupst(shapre, daily_group, cross_mean)
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    f = IntradayTurnoverStd()
    f.result()
    cal_factor(numd={})
