# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File :UpDownTradenumSkewRatio_5m.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class UpDownTradenumSkewRatio_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = ''
    extend_days = 1
    author = 'lzc'
    logic = '上行主买成交笔数占比的偏度/下行主卖成交占比的偏度 并计算 分组比例 昨日T时刻到当日T时刻为一天'
    article = ''
    freq = '5mins'
    basic_datas = {'daily': ['free_float_shares', 'close'], '30mins': [], '5mins': ['buytradenum', 'tradenum', 'selltradenum', 'close'], '1min': []}

    window = 15

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return [self.database['5mins'][x] for x in ['buytradenum', 'tradenum', 'selltradenum', 'close']]

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        buytradenum, tradenum, selltradenum, close = self.st_factor()
        daily_group = sameshape(buytradenum, self.group_factor())
        free_float_cap = self.database['daily']['free_float_shares'] * self.database['daily']['close']
        free_float_cap = delay(free_float_cap, 1)

        buytradenum_ratio = buytradenum / tradenum
        selltradenum_ratio = selltradenum / tradenum

        ret = close / delay(close.swapaxes(0, 1)).swapaxes(0, 1) - 1
        up = ret > 0
        up_ratio = np.where(up, buytradenum_ratio, np.nan)
        down_ratio = np.where(up, np.nan, selltradenum_ratio)

        import bottleneck
        def intrad_past_day_rolling_sum(x_, finit=None):
            shape = x_.shape
            if finit is None:
                finit = np.isfinite(x_)
            x = np.where(finit, x_, 0)
            return bottleneck.move_sum(np.concatenate([delay(x, 1), x], axis=1), window=shape[1], axis=1)[:, -shape[1]:, :]

        def get_group_std_and_stk_std(X):
            finit_tag = np.isfinite(X)
            X = np.where(finit_tag, X, 0)
            X2 = X ** 2
            X3 = X ** 3

            SUMX = intrad_past_day_rolling_sum(X)
            SUMX2 = intrad_past_day_rolling_sum(X2)
            SUMX3 = intrad_past_day_rolling_sum(X3)
            COUNT = intrad_past_day_rolling_sum(finit_tag)
            group_count = st2groupst(COUNT, daily_group, cross_sum)
            group_EX3 = st2groupst(SUMX3, daily_group, cross_sum)
            group_SUMX = st2groupst(SUMX, daily_group, cross_sum)
            group_mean = group_SUMX / group_count
            group_std = (group_count * st2groupst(SUMX2, daily_group, cross_sum) - group_mean ** 2) / group_count ** 2

            stk_mean = SUMX / COUNT
            stk_EX3 = SUMX3 / COUNT
            stk_std = (COUNT * SUMX2 - SUMX * SUMX) / COUNT ** 2

            stk_skew = (stk_EX3 - 3 * stk_mean * stk_std - stk_mean ** 3) / stk_std ** 0.5
            group_skew = (group_EX3 - 3 * group_mean * group_std - group_mean ** 3) / group_std ** 1.5
            return stk_skew, group_skew

        up_stk_skew, up_group_skew = get_group_std_and_stk_std(up_ratio)
        down_stk_skew, down_group_skew = get_group_std_and_stk_std(down_ratio)

        return arr_match_index((up_stk_skew * up_group_skew) / (down_stk_skew * down_group_skew), self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    # f = UpDownAmtVolRatio()
    # f.result()
    cal_factor()
