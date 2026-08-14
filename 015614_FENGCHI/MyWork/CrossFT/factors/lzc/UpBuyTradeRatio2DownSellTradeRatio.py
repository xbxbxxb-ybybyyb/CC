# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : UpBuyTradeRatio2DownSellTradeRatio.py
import sys

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class UpBuyTradeRatio2DownSellTradeRatio(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 15
    author = 'lzc'
    logic = '上行主动买成占比均值与下行主动卖出成交占比均值之比 * 分组的该值'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['free_float_shares'], '30mins': [], '5mins': ['buytradeamt', 'selltradeamt', 'amt', 'close'], '1min': []}

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
        buytradeamt, selltradeamt, amt, close = [self.database['5mins'][x] for x in
                                                 ['buytradeamt', 'selltradeamt', 'amt', 'close']]
        free_float_shares = self.database['daily']['free_float_shares']
        daily_group = sameshape(free_float_shares, self.group_factor())
        minute_group = sameshape(buytradeamt, self.group_factor())

        buytradeamt_ratio = buytradeamt / amt
        selltradeamt_ratio = selltradeamt / amt

        ret = close / delay(close, 1) - 1

        up_buytradeamt_ratio = np.where(ret > 0, buytradeamt_ratio, np.nan)
        down_selltradeamt_ratio = np.where(ret > 0, np.nan, selltradeamt_ratio)

        factor = np.nanmean(up_buytradeamt_ratio, axis=1) / np.nanmean(down_selltradeamt_ratio, axis=1)
        factor_stk = factor[:, None, :]

        factor_group = st2groupst(factor_stk, daily_group, cross_mean)

        return arr_match_index(factor_stk * factor_group, self.cal_date_range, self.date_range)

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
    f = UpBuyTradeRatio2DownSellTradeRatio()
    e = time.time()
    # f.result()
    f.result()
    print(f'total calc time {time.time() - e}')
    # send_message(['015664'],f'total calc time {time.time()-e}')
