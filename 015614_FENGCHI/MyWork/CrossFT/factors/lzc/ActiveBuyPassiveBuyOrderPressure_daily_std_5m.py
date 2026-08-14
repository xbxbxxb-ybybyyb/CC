# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : ActiveBuyPassiveBuyOrderPressure_daily_std.py

import sys

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class ActiveBuyPassiveBuyOrderPressure_daily_std_5m(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 15
    author = 'lzc'
    logic = '新增主动委托买入量/新增被动买入量 *  行业用自由流通股本折算后的量之比  日内波动'
    article = ''
    freq = '5mins'
    basic_datas = {'daily': ['free_float_shares'], '30mins': [], '5mins': ['passivebuyordervol', 'activebuyordervol'], '1min': []}

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return  # self.database['5mins']['close_badj']

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        passivebuyordervol, activebuyordervol = [self.database['5mins'][x] for x in ['passivebuyordervol', 'activebuyordervol']]
        free_float_shares = self.database['daily']['free_float_shares']
        daily_group = sameshape(free_float_shares, self.group_factor())
        minute_group = sameshape(passivebuyordervol, self.group_factor())

        import bottleneck
        def intrad_past_day_rolling_sum(x_, finit=None):
            shape = x_.shape
            if finit is None:
                finit = np.isfinite(x_)
            x = np.where(finit, x_, 0)
            return bottleneck.move_sum(np.concatenate([delay(x, 1), x], axis=1), window=shape[1], axis=1)[:, -shape[1]:, :]

        def intrad_past_day_rolling_std(x, finit=None):
            if finit is None:
                finit = np.isfinite(x)
            SUM = intrad_past_day_rolling_sum(np.where(finit, x, 0))
            SUM2 = intrad_past_day_rolling_sum(np.where(finit, x ** 2, 0))
            COUNT = intrad_past_day_rolling_sum(finit)
            return (SUM2 / COUNT - (SUM / COUNT) ** 2) ** 0.5

        stk_pressure = activebuyordervol / passivebuyordervol
        group_pressure = st2groupst(activebuyordervol / free_float_shares, minute_group, cross_sum) / st2groupst(passivebuyordervol / free_float_shares, minute_group, cross_sum)
        # factor = np.nanstd(stk_pressure * group_pressure, axis=1)[:, None, :]
        factor = intrad_past_day_rolling_std(stk_pressure) * intrad_past_day_rolling_std(group_pressure)
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    # for group in groups:
    #     for func in funcs:
    #         print('-------------{}-----------{}-------------'.format(group,func))
    cal_factor()
