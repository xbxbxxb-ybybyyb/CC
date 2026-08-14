# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File :IntradayTurnoverStd_5m.py

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class IntradayTurnoverStd_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 45
    author = 'lzc'
    logic = '日内分钟K换手率波动率近30日sharpe 前日T时刻到当日T时刻为一天'
    article = ''
    freq = '5mins'
    basic_datas = {'daily': ['free_float_shares', 'close'], '30mins': [], '5mins': ['amt'], '1min': []}

    window = 30

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return [self.database['5mins'][x] for x in ['amt']] + [self.database['daily'][x] for x in ['free_float_shares', 'close']]

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        amt, free_float_shares, close = self.st_factor()
        daily_group = sameshape(amt, self.group_factor())

        shape = close.shape
        import bottleneck
        intrad_past_day_rolling_sum = lambda x: bottleneck.move_sum(np.concatenate([delay(x, 1), x], axis=1), window=shape[1], axis=1)[:, -shape[1]:, :]

        def intrad_past_day_rolling_std(x, finit=None):
            if finit is None:
                finit = np.isfinite(x)
            SUM = intrad_past_day_rolling_sum(np.where(finit, x, 0))
            SUM2 = intrad_past_day_rolling_sum(np.where(finit, x ** 2, 0))
            COUNT = intrad_past_day_rolling_sum(finit)
            return SUM2 / COUNT - (SUM / COUNT) ** 2

        turover = amt / delay(free_float_shares, 1) / delay(close, 1)
        intraday_std = intrad_past_day_rolling_std(turover)

        std_finit = np.isfinite(intraday_std)
        X = np.where(std_finit, intraday_std, 0)

        SUMX = bottleneck.move_sum(X.sum(axis=1), window=self.window, axis=0)
        SUMX2 = bottleneck.move_sum((X ** 2).sum(axis=1), window=self.window, axis=0)
        COUNT = bottleneck.move_sum(std_finit.sum(axis=1), window=self.window, axis=0)
        recent_30day_mean = SUMX / COUNT
        recent_30day_std = SUMX2 / COUNT - recent_30day_mean ** 2
        recent_30day_mean, recent_30day_std = delay(recent_30day_mean[:, None, :], 1), delay(recent_30day_std[:, None, :], 1)

        shapre = (intraday_std - recent_30day_mean) / recent_30day_std
        factor = shapre * st2groupst(shapre, daily_group, cross_mean)
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    # f = IntradayTurnoverStd()
    # f.result()
    cal_factor(numd={})
