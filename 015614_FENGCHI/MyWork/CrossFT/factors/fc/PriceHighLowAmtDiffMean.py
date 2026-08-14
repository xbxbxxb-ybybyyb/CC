# coding: utf-8
# Author：fengchi863
# Date ：2021/9/24 14:47

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class PriceHighLowAmtDiffMean(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 0
    author = 'fc'
    freq = 'daily'
    logic = '成交在当日高位的成交量 / 成交在当日价格低位的成交量 组内求平均'
    article = ''
    basic_datas = {'daily': ['high_badj', 'low_badj'], '30mins': [], '5mins': [], '1min': ['amt', 'close_badj']}

    def st_factor(self):
        amt = self.database['1min']['amt']
        close = self.database['1min']['close_badj']
        high = self.database['daily']['high_badj']
        low = self.database['daily']['low_badj']
        price_median = np.repeat((high + low) / 2, 242, axis=1)

        low_part = close <= price_median
        high_part = close >= price_median

        amt_low = np.nansum(amt * low_part, axis=1, keepdims=True)
        amt_high = np.nansum(amt * high_part, axis=1, keepdims=True)

        ret = amt_high / amt_low
        return ret

    def calc_groupst(self):
        ret = self.st_factor()
        group = sameshape(ret, self.group_factor())
        ret = st2groupst(ret, group, cross_mean)
        factor = arr_match_index(ret, self.cal_date_range, self.date_range)
        return factor

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    f = PriceHighLowAmtDiffMean()
    print(f.result())
    f.save_result()
