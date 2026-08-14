# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File :VolSwing5mToAll.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class VolSwing5mToAll(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 0
    author = 'lzc'
    logic = '最后5分钟成交量振幅/全天成交量振幅 个股值*分组值'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['free_float_shares'], '30mins': [], '5mins': ['close', 'amt'], '1min': []}

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
        # daily_group = sameshape(self.database['daily']['free_float_shares'], self.group_factor())
        minute_group = sameshape(amt, self.group_factor())

        group_amt = st2groupst(amt, minute_group, cross_sum)

        stk_last_5m_swing = abs(amt[:, -1, :] - amt[:, -2, :])[:, None, :]
        group_last5min_swaing = abs(group_amt[:, -1, :] - group_amt[:, -2, :])[:, None, :]

        stk_daily_swing = (np.nanmax(amt, axis=1) - np.nanmin(amt, axis=1))[:, None, :]
        group_daily_swing = (np.nanmax(group_amt, axis=1) - np.nanmin(group_amt, axis=1))[:, None, :]

        return arr_match_index((stk_last_5m_swing * group_last5min_swaing) / (stk_daily_swing * group_daily_swing), self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    # f = VolSwing5mToAll()
    # f.result()
    cal_factor(numd={})
