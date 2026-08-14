# coding: utf-8
# Author：fengchi863
# Date ：2021/9/6 11:03

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *
import talib

'''
一种方式：ZSCORE
'''


class WillRJZScore(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 20
    author = 'fc'
    freq = 'daily'
    logic = '行业内个股的威廉指标ZScore'
    article = ''
    basic_datas = {'daily': ['close_badj', 'high_badj', 'low_badj'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        close = self.database['daily']['close_badj']
        high = self.database['daily']['high_badj']
        low = self.database['daily']['low_badj']
        close = pd.DataFrame(close[:, 0, :], index=self.cal_date_range, columns=self.code_list)
        high = pd.DataFrame(high[:, 0, :], index=self.cal_date_range, columns=self.code_list)
        low = pd.DataFrame(low[:, 0, :], index=self.cal_date_range, columns=self.code_list)
        willr = {}
        for stk in close.columns:
            try:
                willr[stk] = talib.WILLR(high[stk].values, low[stk].values, close[stk].values)
            except:
                willr[stk] = np.array([np.nan] * len(close.index))
        ret = pd.DataFrame(willr)
        ret.index = close.index
        return ret.values.reshape(ret.shape[0], 1, -1)

    def calc_groupst(self):
        ret = self.st_factor()
        self.group = sameshape(ret, self.group_factor())

        MEAN = st2groupst(ret, self.group, cross_mean)
        STD = st2groupst(ret, self.group, cross_std)
        ret = (ret - MEAN) / STD
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    cal_factor()
