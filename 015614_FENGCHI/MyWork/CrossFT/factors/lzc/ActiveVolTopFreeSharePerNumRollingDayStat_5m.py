# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : ActiveVolTopFreeSharePerNumRollingDayStat_5m.py
import sys

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class ActiveVolTopFreeSharePerNumRollingDayStat_5m(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 15
    author = 'lzc'
    logic = '平均每笔成交量占自由流通股本的比例 * 行业平均每笔成交占行业总自由流通股本的比例 过去T时刻到当日T时刻为一日'
    article = ''
    freq = '5mins'
    basic_datas = {'daily': ['free_float_shares'], '30mins': [], '5mins': ['buytradevol', 'selltradevol', 'tradenum'], '1min': []}

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
        tradenum, buytradevol, selltradevol = [self.database['5mins'][x] for x in
                                               ['tradenum', 'buytradevol', 'selltradevol']]
        free_float_shares = self.database['daily']['free_float_shares']
        free_float_shares = delay(free_float_shares)
        # daily_group = sameshape(free_float_shares, self.group_factor())
        minute_group = sameshape(buytradevol, self.group_factor())

        import bottleneck
        def intrad_past_day_rolling_sum(x, finit=None):
            if finit is None:
                finit = np.isfinite(x)
            shape = x.shape
            x = np.where(finit, x, 0)
            return bottleneck.move_sum(np.concatenate([delay(x, 1), x], axis=1), window=shape[1], axis=1)[:, -shape[1]:, :]

        total_trade_vol = intrad_past_day_rolling_sum(buytradevol + selltradevol)
        total_tradenum = intrad_past_day_rolling_sum(tradenum)
        vol_percent_per_num = total_trade_vol / total_tradenum / free_float_shares

        group_vol_percent_per_num = st2groupst(total_trade_vol / free_float_shares, minute_group, cross_sum) / st2groupst(total_tradenum, minute_group, cross_sum)

        return arr_match_index(group_vol_percent_per_num * vol_percent_per_num, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    cal_factor()
