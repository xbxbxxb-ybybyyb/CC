# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File :IntradtayAmtWeightedProfit.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class IntradtayAmtWeightedProfit(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 0
    author = 'lzc'
    logic = '成交额为权重计算所有浮盈bar的平均收益率 并与 分组的该收益复利'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['free_float_shares'], '30mins': [], '5mins': ['close', 'amt'], '1min': []}

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
        self.group = sameshape(self.database['daily']['free_float_shares'], self.group_factor())
        ret = (close.swapaxes(0, 1) / delay(close.swapaxes(0, 1), 1)).swapaxes(0, 1) - 1
        down_tag = ret > 0
        down_ret = np.where(down_tag, ret, 0)
        down_amt = np.where(down_tag, amt, 0)
        wheited_down_ret = np.nansum(down_ret * down_amt, axis=1)[:, None, :]
        down_amt_daily = np.nansum(down_tag * down_amt, axis=1)[:, None, :]

        stk_amt_weighted_ret = wheited_down_ret / down_amt_daily
        group_weighted_down_ret = st2groupst(wheited_down_ret, self.group, cross_sum) / st2groupst(down_amt_daily, self.group, cross_sum)
        factor = (1 + stk_amt_weighted_ret) * (1 + group_weighted_down_ret)

        return arr_match_index(factor, self.cal_date_range, self.date_range)

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
