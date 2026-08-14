# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File :IntradtayAmtWeightedProfit_5m.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class IntradtayAmtWeightedProfit_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 0
    author = 'lzc'
    logic = '成交额为权重计算所有浮盈bar的平均收益率 并与 分组的该收益复利 前一日T时刻到当日T时刻当作一天'
    article = ''
    freq = '5mins'
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
        self.group = sameshape(close, self.group_factor())

        shape = close.shape
        import bottleneck
        intrad_past_day_rolling_sum = lambda x: bottleneck.move_sum(np.concatenate([delay(x, 1), x], axis=1), window=shape[1], axis=1)[:, -shape[1]:, :]

        shape = close.shape
        import bottleneck
        intrad_past_day_rolling_sum = lambda x: bottleneck.move_sum(np.concatenate([delay(x, 1), x], axis=1), window=shape[1], axis=1)[:, -shape[1]:, :]

        ret = (close.swapaxes(0, 1) / delay(close.swapaxes(0, 1), 1)).swapaxes(0, 1) - 1
        down_tag = ret > 0
        down_ret = np.where(down_tag, ret, 0)
        down_amt = np.where(down_tag, amt, 0)
        wheited_down_ret = intrad_past_day_rolling_sum(down_ret * down_amt)
        down_amt_daily = intrad_past_day_rolling_sum(down_tag * down_amt)

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
