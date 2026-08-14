# coding: utf-8
# Author：fengchi863
# Date ：2021/8/17 14:18

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *


class NewLowPct1y(crossFactor):
    cross_group = None
    cross_func = None
    extend_days = 260
    author = 'fc'
    freq = 'daily'
    logic = '创新低的个股比'
    basic_datas = {'daily': ['close_badj']}

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        close = self.database['daily']['close_badj']
        expanding_low = dt_min(close, 252)
        low_num = close == expanding_low
        total = np.nansum(close, axis=-1)
        ret = np.nansum(low_num, axis=-1) / total
        factor = arr_match_index(index2st(ret, len(self.code_list)), self.cal_date_range, self.date_range)
        return factor

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.st_factor()


if __name__ == '__main__':
    val1 = cal_factor(numd={})
    val2 = cal_factor(numd={'daily': 10})
    gap = abs(val1 - val2)
    print(np.nansum(gap))
