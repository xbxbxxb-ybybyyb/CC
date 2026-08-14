# coding: utf-8
# Author：fengchi863
# Date ：2021/8/17 14:48

import talib

from basic.crossFactor import crossFactor
from basic.crossUtils import *


class CybzMacd(crossFactor):
    cross_group = None
    cross_func = None
    extend_days = 260
    author = 'fc'
    factor_name = 'CybzMacd'
    freq = 'daily'
    logic = '创业板指MACD'
    article = '市场监控结论'
    basic_datas = {'daily': ['close_CYBZ']}

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        close = self.database['daily']['close_CYBZ'][:, 0, 0]
        _, _, a3 = talib.MACD(close, fastperiod=12,
                              slowperiod=26, signalperiod=9)
        a = index2st(a3.reshape(-1, 1), len(self.code_list))

        return arr_match_index(a, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.st_factor()


if __name__ == '__main__':
    # f = CybzMacd()
    # f.save_result()
    cal_factor()
