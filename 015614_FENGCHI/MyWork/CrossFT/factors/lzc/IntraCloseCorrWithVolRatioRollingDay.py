# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File :IntraCloseCorrWithVolRatioRollingDay.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *
from basic.operators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class IntraCloseCorrWithVolRatioRollingDay(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 0
    author = 'lzc'
    logic = '日内5分钟close 与 Vol占比 *分组因子值'
    article = ''
    freq = '5mins'
    basic_datas = {'daily': ['free_float_shares', 'volume'], '30mins': [], '5mins': ['close', 'vol'], '1min': []}

    window = 15

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return [self.database['5mins'][x] for x in ['close', 'vol']]

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        close, volume = self.st_factor()
        free_float_shares = self.database['daily']['free_float_shares']
        daily = sameshape(close, self.group_factor())
        # minute = sameshape(volume, self.group_factor())

        Y = volume / np.nansum(volume, axis=1)[:, None, :]
        X = close / close[:, [0], :]

        count = np.isfinite(X) & np.isfinite(Y)
        X = np.where(count, X, 0)
        Y = np.where(count, Y, 0)

        SUMX2 = dt_sum(X ** 2, 48)
        SUMY2 = dt_sum(Y ** 2, 48)
        SUMXY = dt_sum(X * Y, 48)
        SUMY = dt_sum(Y, 48)
        SUMX = dt_sum(X, 48)
        COUNT = dt_sum(count, 48)

        stk_corr = (COUNT * SUMXY - SUMY * SUMX) / (COUNT * SUMX2 - SUMX ** 2) ** 0.5 / (COUNT * SUMY2 - SUMY ** 2) ** 0.5

        group_COUNT = st2groupst(COUNT, daily, cross_sum)
        group_SUMX2 = st2groupst(SUMX2, daily, cross_sum)
        group_SUMY2 = st2groupst(SUMY2, daily, cross_sum)
        group_SUMXY = st2groupst(SUMXY, daily, cross_sum)
        group_SUMY = st2groupst(SUMY, daily, cross_sum)
        group_SUMX = st2groupst(SUMX, daily, cross_sum)

        group_corr = (group_COUNT * group_SUMXY - group_SUMY * group_SUMX) / (group_COUNT * group_SUMX2 - group_SUMX ** 2) ** 0.5 / (
                group_COUNT * group_SUMY2 - group_SUMY ** 2) ** 0.5

        return arr_match_index(stk_corr * group_corr, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    cal_factor()
