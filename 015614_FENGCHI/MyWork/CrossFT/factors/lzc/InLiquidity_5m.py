# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File :InLiquidity_5m.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class InLiquidity_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 2
    author = 'lzc'
    logic = '个股非流动性*分组值 前日T时刻到当日T时刻为一日'
    article = ''
    freq = '5mins'
    basic_datas = {'daily': ['free_float_shares', 'volume', 'close'], '30mins': [], '5mins': ['close', 'vol', 'high', 'low', 'close_badj'], '1min': []}

    window = 15

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return [self.database['5mins'][x] for x in ['close', 'vol', 'high', 'low', 'close_badj']]

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        close, vol, high, low, close_badj = self.st_factor()
        free_float_shares = delay(self.database['daily']['free_float_shares'], 1)
        # turn = vol*close/delay(self.database['daily']['free_float_shares']*self.database['daily']['close'],1)

        import bottleneck
        def intrad_past_day_rolling_sum(x_, finit=None):
            shape = x_.shape
            if finit is None:
                finit = np.isfinite(x_)
            x = np.where(finit, x_, 0)
            return bottleneck.move_sum(np.concatenate([delay(x, 1), x], axis=1), window=shape[1], axis=1)[:, -shape[1]:, :]

        past_day_amt = intrad_past_day_rolling_sum(close * vol)
        past_day_turn = past_day_amt / free_float_shares
        ret = close_badj / delay(close_badj) - 1
        inliquidity = abs(ret) / past_day_turn

        daily = sameshape(free_float_shares, self.group_factor())
        minute = sameshape(close, self.group_factor())
        # minute = sameshape(volume, self.group_factor())
        group_turn = st2groupst(past_day_amt, minute, cross_sum) / st2groupst(free_float_shares, daily, cross_sum)
        group_ret = st2groupst(abs(ret), minute, cross_mean)
        group_inliquidity = group_ret / group_turn

        return arr_match_index(group_inliquidity * inliquidity, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    cal_factor()
