# coding: utf-8
# Author：fengchi863
# Date ：2021/8/17 14:20

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *


class NewHighDivLow1y_5m(crossFactor):
    cross_group = None
    cross_func = None
    extend_days = 260
    author = 'fc'
    freq = '5mins'
    logic = '新高和新低的个股比'
    basic_datas = {'daily': ['close_badj'], '30mins': [], '5mins': ['close_badj'], '1min': []}

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        epsilon = 1e-1
        daily_close = self.database['daily']['close_badj']
        min_close = self.database['5mins']['close_badj']
        expanding_high = dt_max(daily_close, 252)
        expanding_low = dt_min(daily_close, 252)
        min_close_min = dt_min(min_close, 48)
        min_close_max = dt_max(min_close, 48)

        ret1 = (min_close > expanding_high) & (min_close == min_close_max)
        ret2 = (min_close < expanding_low) & (min_close == min_close_min)
        pct_factor = ret1.sum(axis=2) / (ret2.sum(axis=2) + epsilon)
        factor = arr_match_index(np.repeat(pct_factor[:, :, None], len(self.code_list), axis=2), self.cal_date_range, self.date_range)
        return factor

    def result(self):
        return self.st_factor()


if __name__ == '__main__':
    # f = NewHighDivLow1y_5m()
    # print(f.result())

    cal_factor()
