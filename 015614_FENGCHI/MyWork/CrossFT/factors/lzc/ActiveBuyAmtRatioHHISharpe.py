# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File :ActiveBuyAmtRatioHHISharpe.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class ActiveBuyAmtRatioHHISharpe(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 1
    author = 'lzc'
    logic = '日内主动买入成交额占比的HHI指数截面sharpe'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['free_float_shares', 'close'], '30mins': [], '5mins': ['amt', 'buytradeamt'], '1min': []}

    window = 15

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return [self.database['5mins'][x] for x in ['amt', 'buytradeamt']]

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        amt, buytradeamt = self.st_factor()
        buytrade_ratio = buytradeamt / amt
        daily_factor = sameshape(self.database['daily']['free_float_shares'], self.group_factor())
        pct = buytrade_ratio / np.nansum(buytrade_ratio, axis=1)[:, None, :]
        hhi = np.nansum(pct ** 2, axis=1)[:, None, :]
        factor = (hhi - st2groupst(hhi, daily_factor, cross_mean)) / st2groupst(hhi, daily_factor, cross_std)
        return arr_match_index(factor, self.cal_date_range, self.date_range)

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
