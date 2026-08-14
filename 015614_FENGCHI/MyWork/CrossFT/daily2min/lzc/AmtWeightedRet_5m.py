# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File :AmtWeightedRet_5m.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class AmtWeightedRet_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 2
    author = 'lzc'
    logic = '日内成交额加权平均收益 个股值*分组值   按昨日 T时刻到今日T时刻为一日计算'
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
        daily_group = sameshape(close, self.group_factor())
        ret = close / delay(close.swapaxes(0, 1), 1).swapaxes(0, 1) - 1
        shape = close.shape
        import bottleneck
        intrad_past_day_rolling_sum = lambda x: bottleneck.move_sum(np.concatenate([delay(x, 1), x], axis=1), window=shape[1], axis=1)[:, -shape[1]:, :]

        ret_finit = np.isfinite(ret)
        amt_finit = np.isfinite(amt)
        both_finit = ret_finit & amt_finit

        X = np.where(both_finit, ret, 0)
        y = np.where(both_finit, amt, 0)
        inter_ret = intrad_past_day_rolling_sum(X * y)
        daily_amt = intrad_past_day_rolling_sum(y)
        stk_weighed_ret = inter_ret / daily_amt
        group_weighted_ret = st2groupst(inter_ret, daily_group, cross_sum) / st2groupst(daily_amt, daily_group, cross_sum)

        return arr_match_index(stk_weighed_ret * group_weighted_ret, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    # f = AmtWeightedRet_5m()
    # f.result()
    cal_factor(numd={})
