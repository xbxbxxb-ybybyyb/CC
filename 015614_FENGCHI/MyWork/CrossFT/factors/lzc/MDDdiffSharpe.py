# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File :MDDdiffSharpe.py

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class MDDdiffSharpe(crossFactor):
    cross_group = 'sw1'
    cross_func = ''
    extend_days = 0
    author = 'lzc'
    logic = '日内最大回撤相对前日最大回撤截面sharpe'
    article = ''
    freq = 'daily'
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

        close_5min = pd.Panel(self.database['5mins']['close']).fillna(method='pad', axis=1).values
        ret_5min = close_5min - delay(close_5min.swapaxes(0, 1)).swapaxes(0, 1)

        daily_group = sameshape(self.database['daily']['free_float_shares'], self.group_factor())

        mdd = np.nanmax(np.maximum.accumulate(close_5min, axis=1) / close_5min - 1, axis=1)[:, None, :]
        mdd_pre = delay(mdd, 1)
        mdd_diff = mdd - mdd_pre
        factor = (mdd_diff - st2groupst(mdd_diff, daily_group, cross_mean)) / st2groupst(mdd_diff, daily_group, cross_std)

        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    f = MDDdiffSharpe()
    f.result()
    cal_factor(numd={})
