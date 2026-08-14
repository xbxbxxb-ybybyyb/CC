# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : ActiveVolTopFreeSharePerNum.py
import sys

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class ActiveVolTopFreeSharePerNum(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 15
    author = 'lzc'
    logic = '平均每笔成交量占自由流通股本的比例 * 行业平均每笔成交占行业总自由流通股本的比例'
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
        daily_group = sameshape(free_float_shares, self.group_factor())
        minute_group = sameshape(buytradevol, self.group_factor())

        vol_percent_per_num = (buytradevol + selltradevol) / free_float_shares / tradenum

        group_vol_percent_per_num = st2groupst((buytradevol + selltradevol) / free_float_shares, minute_group, cross_sum) / st2groupst(tradenum, minute_group, cross_sum)

        return arr_match_index(group_vol_percent_per_num * vol_percent_per_num, self.cal_date_range, self.date_range)

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
    f = ActiveVolTopFreeSharePerNum()
    e = time.time()
    # f.result()
    f.save_result()
    print(f'total calc time {time.time() - e}')
    # send_message(['015664'],f'total calc time {time.time()-e}')
