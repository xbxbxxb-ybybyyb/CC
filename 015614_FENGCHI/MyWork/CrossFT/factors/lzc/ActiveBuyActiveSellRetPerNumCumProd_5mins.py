# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : ActiveBuyActiveSellRetPerNumCumProd_5mins.py
import sys

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class ActiveBuyActiveSellRetPerNumCumProd_5mins(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 15
    author = 'lzc'
    logic = '主动买入均价对主动卖出均价的单笔收益率 与行业的该收益率复利'
    article = ''
    freq = '5mins'
    basic_datas = {'daily': ['free_float_shares'], '30mins': [], '5mins': ['buytradevol', 'buytradeamt', 'selltradevol', 'selltradeamt', 'tradenum'], '1min': []}

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
        tradenum, buytradevol, buytradeamt, selltradevol, selltradeamt = [self.database['5mins'][x] for x in
                                                                          ['tradenum', 'buytradevol', 'buytradeamt', 'selltradevol', 'selltradeamt']]
        free_float_shares = self.database['daily']['free_float_shares']
        daily_group = sameshape(free_float_shares, self.group_factor())
        minute_group = sameshape(buytradevol, self.group_factor())

        buy_vwap, sell_vwap = buytradeamt / buytradevol, selltradeamt / selltradevol

        ret = sell_vwap / buy_vwap - 1

        ret_per_num = ret / tradenum
        group_ret_per_num = st2groupst(ret_per_num * free_float_shares, minute_group, cross_sum) / st2groupst(free_float_shares, daily_group, cross_sum)

        factor = (1 + ret_per_num) * (1 + group_ret_per_num) - 1
        # std = np.nanstd(active, axis=1)[:, None, :]

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
    f = ActiveBuyActiveSellRetPerNumCumProd_5mins()
    e = time.time()
    # f.result()
    f.save_result()
    print(f'total calc time {time.time() - e}')
    # send_message(['015664'],f'total calc time {time.time()-e}')
