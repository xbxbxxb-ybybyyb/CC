# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File :ThirdMomentAcross5DayVolatility.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class ThirdMomentAcross5DayVolatility(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 6
    author = 'lzc'
    logic = '日内累计收益率三阶矩剔除5日波动率  行业面板三阶矩剔除行业5日面板波动率'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['close_badj'], '30mins': [], '5mins': ['close'], '1min': []}

    window = 15

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return self.database['5mins']['close'], self.database['daily']['close_badj']

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        close_minute, close_daily = self.st_factor()
        daily_group = sameshape(close_daily, self.group_factor())
        daily_minute = sameshape(close_daily, self.group_factor())

        stk_cumret = close_minute / close_minute[:, [0], :] - 1
        stk_cumret_finite = np.isfinite(stk_cumret)
        stk_cumret = np.where(stk_cumret_finite, stk_cumret, 0)

        daily_ret = close_daily / delay(close_daily, 1) - 1
        day_5_extend = (daily_ret,)
        for i in range(1, 5):
            day_5_extend += (delay(daily_ret, i),)
        day_5_extend = np.concatenate(day_5_extend, axis=1)
        day_5_extend_finit = np.isfinite(day_5_extend)
        Y = np.where(day_5_extend_finit, day_5_extend, 0)
        Y2 = Y ** 2

        SUMY = np.nansum(Y, axis=1)[:, None, :]
        SUMY2 = np.nansum(Y2, axis=1)[:, None, :]
        NY = np.nansum(day_5_extend_finit, axis=1)[:, None, :]
        stk_5day_vol = SUMY2 / NY - (SUMY / NY) ** 2
        group_NY = st2groupst(NY, daily_group, cross_sum)
        group_5day_vol = st2groupst(SUMY2, daily_group, cross_sum) / group_NY - (st2groupst(SUMY, daily_group, cross_sum) / group_NY) ** 2

        X3 = stk_cumret ** 3
        NX = np.nansum(stk_cumret_finite, axis=1)[:, None, :]
        SUMX3 = np.nansum(X3, axis=1)[:, None, :]
        stk_3m = SUMX3 / NX
        group_3m = st2groupst(SUMX3, daily_group, cross_sum) / st2groupst(NX, daily_group, cross_sum)

        stk_factor = stk_3m - stk_5day_vol
        group_factor = group_3m - group_5day_vol

        return arr_match_index(group_factor * stk_factor, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    # f = IntradtayAmtWeightedLoss()
    # f.result()
    cal_factor(numd={})
