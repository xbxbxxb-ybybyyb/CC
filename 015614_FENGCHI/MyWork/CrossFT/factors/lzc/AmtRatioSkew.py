# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File :AmtRatioSkew.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class AmtRatioSkew(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 1
    author = 'lzc'
    logic = '成交额占前日自由流通市值的偏度 个股日内偏度*分组面板偏度'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['free_float_shares', 'close'], '30mins': [], '5mins': ['amt'], '1min': []}

    window = 15

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return [self.database['5mins'][x] for x in ['amt']]

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        amt, = self.st_factor()
        daily_group = sameshape(self.database['daily']['free_float_shares'], self.group_factor())
        free_float_cap = self.database['daily']['free_float_shares'] * self.database['daily']['close']
        free_float_cap = delay(free_float_cap, 1)

        netlize_amt = amt / free_float_cap
        finit_tag = np.isfinite(netlize_amt)
        X = np.where(finit_tag, netlize_amt, 0)
        X2 = X ** 2
        X3 = X ** 3

        SUMX = np.nansum(X, axis=1)[:, None, :]
        SUMX2 = np.nansum(X2, axis=1)[:, None, :]
        SUMX3 = np.nansum(X3, axis=1)[:, None, :]
        COUNT = np.nansum(finit_tag, axis=1)[:, None, :]
        group_count = st2groupst(COUNT, daily_group, cross_sum)
        group_EX3 = st2groupst(SUMX3, daily_group, cross_sum)
        group_SUMX = st2groupst(SUMX, daily_group, cross_sum)
        group_mean = group_SUMX / group_count
        group_std = (group_count * st2groupst(SUMX2, daily_group, cross_sum) - group_mean ** 2) / group_count

        stk_mean = SUMX / COUNT
        stk_EX3 = SUMX3 / COUNT
        stk_std = (COUNT * SUMX2 - SUMX * SUMX) / COUNT ** 2

        stk_skew = (stk_EX3 - 3 * stk_mean * stk_std - stk_mean ** 3) / stk_std ** 0.5
        group_skew = (group_EX3 - 3 * group_mean * group_std - group_mean ** 3) / group_std ** 1.5

        return arr_match_index(group_skew * stk_skew, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    # f = AmtRatioSkew()
    # f.result()
    cal_factor(numd={})
