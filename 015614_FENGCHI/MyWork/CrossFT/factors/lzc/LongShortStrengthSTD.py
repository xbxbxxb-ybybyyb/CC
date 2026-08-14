# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File :LongShortStrengthSTD.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class LongShortStrengthSTD(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 0
    author = 'lzc'
    logic = '分组多空力量波动性 * 个股多空力量波动'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['free_float_shares', 'close'], '30mins': [], '5mins': ['close', 'amt'], '1min': []}

    window = 15

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return [self.database['5mins'][x] for x in ['close', 'amt']]

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        close, amt = self.st_factor()
        daily_group = sameshape(self.database['daily']['free_float_shares'], self.group_factor())
        ret = (close.swapaxes(0, 1) / delay(close.swapaxes(0, 1), 1)).swapaxes(0, 1)
        long_sort_strength = ret * amt

        finit_tag = np.isfinite(long_sort_strength)
        X = np.where(finit_tag, long_sort_strength, 0)
        X2 = X ** 2

        SUMX = np.nansum(X, axis=1)[:, None, :]
        SUMX2 = np.nansum(X2, axis=1)[:, None, :]
        COUNT = np.nansum(finit_tag, axis=1)[:, None, :]

        group_std = (st2groupst(SUMX2, daily_group, cross_sum) - st2groupst(SUMX, daily_group, cross_sum) ** 2) / st2groupst(COUNT, daily_group, cross_sum)
        stk_std = (SUMX2 - SUMX ** 2) / COUNT

        return arr_match_index(group_std * stk_std, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    # f = RelativePriceAbsRetCorr()
    # f.result()
    cal_factor(numd={})
