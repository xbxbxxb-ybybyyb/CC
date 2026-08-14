# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File :Vol5CorrWithRelativeAmt_5m.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *
from basic.operators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class Vol5CorrWithRelativeAmt_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 5
    author = 'lzc'
    logic = '日内5分钟波动率与当日成交额占流通股本之比的相关性 * 个股波动率 滚动240分钟'
    article = ''
    freq = '5mins'
    basic_datas = {'daily': ['free_float_shares', 'volume'], '30mins': [], '5mins': ['close'], '1min': []}

    window = 15

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return [self.database['5mins'][x] for x in ['close']]

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        close, = self.st_factor()
        free_float_shares, vol = self.database['daily']['free_float_shares'], self.database['daily']['volume']
        self.group = sameshape(close, self.group_factor())
        ret = (close.swapaxes(0, 1) / delay(close.swapaxes(0, 1), 1)).swapaxes(0, 1) - 1

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

        def intrad_past_day_rolling_mv(x, finit=None):
            if finit is None:
                finit = np.isfinite(x)
            SUM = intrad_past_day_rolling_sum(np.where(finit, x, 0))
            SUM2 = intrad_past_day_rolling_sum(np.where(finit, x ** 2, 0))
            COUNT = intrad_past_day_rolling_sum(finit)
            return SUM / COUNT, (SUM2 / COUNT - (SUM / COUNT) ** 2) ** 0.5

        _, volatility = intrad_past_day_rolling_mv(ret)

        relative_vol = vol / free_float_shares

        EX = st2groupst(volatility, self.group, cross_mean)
        EY = st2groupst(relative_vol, self.group, cross_mean)
        EX2 = st2groupst(volatility ** 2, self.group, cross_mean)
        EY2 = st2groupst(relative_vol ** 2, self.group, cross_mean)
        EXY = st2groupst(relative_vol * volatility, self.group, cross_mean)
        group_corr = (EXY - EX * EY) / (EX2 - EX ** 2) / (EY2 - EY ** 2)

        return arr_match_index(group_corr * volatility, self.cal_date_range, self.date_range)

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
    cal_factor()
