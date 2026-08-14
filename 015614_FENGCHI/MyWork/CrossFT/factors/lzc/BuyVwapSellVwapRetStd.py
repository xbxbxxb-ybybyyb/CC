# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : BuyVwapSellVwapRetStd.py
import sys


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class BuyVwapSellVwapRetStd(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 15
    author = 'lzc'
    logic = '卖单VWAP对买单VWAP收益率 个股日内波动率 * 分组日内波动率'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['close'], '30mins': [], '5mins': ['buytradevol', 'buytradeamt', 'selltradevol', 'selltradeamt'], '1min': []}

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
        buytradevol, buytradeamt, selltradevol, selltradeamt = [self.database['5mins'][x] for x in ['buytradevol', 'buytradeamt', 'selltradevol', 'selltradeamt']]

        buy_vwap, sell_vwap = buytradeamt / buytradevol, selltradeamt / selltradevol

        ret = sell_vwap / buy_vwap - 1

        stk_std = np.nanstd(ret, axis=1)[:, None, :]

        X = np.nansum(ret, axis=1)[:, None, :]
        X2 = np.nansum(ret ** 2, axis=1)[:, None, :]
        count = np.nansum(~np.isnan(ret), axis=1)[:, None, :]

        daily_group = sameshape(self.database['daily']['close'], self.group_factor())
        SUMX = st2groupst(X, daily_group, cross_sum)
        SUMX2 = st2groupst(X2, daily_group, cross_sum)
        COUNT = st2groupst(count, daily_group, cross_sum)

        group_std = (SUMX2 - SUMX ** 2) / COUNT

        return arr_match_index(group_std * stk_std, self.cal_date_range, self.date_range)

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
    f = BuyVwapSellVwapRetStd()
    e = time.time()
    # f.result()
    f.save_result()
    print(f'total calc time {time.time() - e}')
    # send_message(['015664'],f'total calc time {time.time()-e}')
