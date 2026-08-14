# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : UpdVolPctChange_5m.py

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class UpVolPctChangeDownVolPctChangeRatio_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 32
    author = 'lzc'
    logic = '上行成交额变化率 截面sharpe 与 下行成交额变化率 截面sharpe之比 前一日T时刻到当前交易日为一日'
    article = ''
    freq = '5mins'
    basic_datas = {'daily': ['free_float_shares'], '30mins': [], '5mins': ['vol', 'amt', 'close'], '1min': []}

    window = 15

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return [self.database['5mins'][x] for x in ['vol', 'amt', 'close']]

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        vol, amt, close = self.st_factor()
        daily_group = sameshape(self.database['daily']['free_float_shares'], self.group_factor())
        ret = close / delay(close.swapaxes(0, 1), 1).swapaxes(0, 1) - 1
        up_amt = np.where(ret > 0, amt, 0)

        import bottleneck
        def intrad_past_day_rolling_sum(x):
            shape = x.shape
            # x = np.where(finit, x_)
            return bottleneck.move_sum(np.concatenate([delay(x, 1), x], axis=1), window=shape[1], axis=1)[:, -shape[1]:, :]

        up_amt_daily = intrad_past_day_rolling_sum(up_amt)
        up_amt_pct_change = up_amt_daily / delay(up_amt_daily, 1) - 1
        factor = st2groupst(up_amt_pct_change, daily_group, cross_mean) / st2groupst(up_amt_pct_change, daily_group, cross_std)
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    # f = RoughLongShortStrngthCrossSharpe()
    # f.result()
    cal_factor()
