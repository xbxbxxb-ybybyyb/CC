# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File :SwingCorrWithRankNetlizePrice_5m.py

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class SwingCorrWithRankNetlizePrice_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = ''
    extend_days = 5
    author = 'lzc'
    logic = '日内最大涨幅or最大跌幅与日内波动率 * 最大涨跌幅*波动率 前日T时刻到当日T时刻为1天'
    article = ''
    freq = '5mins'
    basic_datas = {'daily': ['free_float_shares', 'close', 'high', 'low'], '30mins': [], '5mins': ['close'], '1min': []}

    window = 15

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return [self.database['daily'][x] for x in ['free_float_shares', 'close', 'high', 'low']]

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        free_float_shares, close, high, low = self.st_factor()
        close_5min = self.database['5mins']['close']
        ret_5min = close_5min - delay(close_5min.swapaxes(0, 1)).swapaxes(0, 1)
        daily_group = sameshape(ret_5min, self.group_factor())
        import bottleneck
        def intrad_past_day_rolling_sum(x_, finit=None):
            shape = x_.shape
            if finit is None:
                finit = np.isfinite(x_)
            x = np.where(finit, x_, 0)
            return bottleneck.move_sum(np.concatenate([delay(x, 1), x], axis=1), window=shape[1], axis=1)[:, -shape[1]:, :]

        def intrad_past_day_rolling_mean(x, finit=None):
            if finit is None:
                finit = np.isfinite(x)
            SUM = intrad_past_day_rolling_sum(np.where(finit, x, 0))
            COUNT = intrad_past_day_rolling_sum(finit)
            return SUM / COUNT

        def intrad_past_day_rolling_std(x, finit=None):
            if finit is None:
                finit = np.isfinite(x)
            SUM = intrad_past_day_rolling_sum(np.where(finit, x, 0))
            SUM2 = intrad_past_day_rolling_sum(np.where(finit, x ** 2, 0))
            COUNT = intrad_past_day_rolling_sum(finit)
            return (SUM2 / COUNT - (SUM / COUNT) ** 2) ** 0.5

        X = intrad_past_day_rolling_std(ret_5min)
        y = (high / low) - 1

        count_X = np.isfinite(X)
        count_y = np.isfinite(y)
        count = count_X & count_y

        X = np.where(count, X, 0)
        y = np.where(count, y, 0)

        X2 = X ** 2
        y2 = y ** 2
        Xy = X * y
        st2groupst(X, daily_group, cross_sum)
        SUM_X = st2groupst(X, daily_group, cross_sum)
        SUM_Y = st2groupst(y, daily_group, cross_sum)
        SUM_XY = st2groupst(Xy, daily_group, cross_sum)
        SUM_X2 = st2groupst(X2, daily_group, cross_sum)
        SUM_Y2 = st2groupst(y2, daily_group, cross_sum)
        SUM_COUNT = st2groupst(count, daily_group, cross_sum)
        inter_group_corr = (SUM_COUNT * SUM_XY - SUM_X * SUM_Y) / ((SUM_COUNT * SUM_X2 - SUM_X ** 2) ** 0.5) / ((SUM_COUNT * SUM_Y2 - SUM_Y ** 2) ** 0.5)
        X = np.where(count, X, np.nan)
        y = np.where(count, y, np.nan)

        return arr_match_index(inter_group_corr * X * y, self.cal_date_range, self.date_range)

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
    cal_factor()
