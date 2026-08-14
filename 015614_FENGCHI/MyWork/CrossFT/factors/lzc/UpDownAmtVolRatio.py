# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File :UpDownAmtVolRatio.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class UpDownAmtVolRatio(crossFactor):
    cross_group = 'sw1'
    cross_func = ''
    extend_days = 1
    author = 'lzc'
    logic = '日内成交额按自由流通市值处理后 计算日内上行波动和下行波动之比 并计算 分组比例'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['free_float_shares', 'close'], '30mins': [], '5mins': ['amt', 'close'], '1min': []}

    window = 15

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return [self.database['5mins'][x] for x in ['amt', 'close']]

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        amt, close = self.st_factor()
        daily_group = sameshape(self.database['daily']['free_float_shares'], self.group_factor())
        free_float_cap = self.database['daily']['free_float_shares'] * self.database['daily']['close']
        free_float_cap = delay(free_float_cap, 1)

        netlize_amt = amt / free_float_cap
        ret = close / delay(close.swapaxes(0, 1)).swapaxes(0, 1) - 1
        up = ret > 0
        up_amt = np.where(up, netlize_amt, np.nan)
        down_amt = np.where(up, np.nan, netlize_amt)

        def get_group_std_and_stk_std(X):
            finit_tag = np.isfinite(X)
            X = np.where(finit_tag, X, 0)
            X2 = X ** 2
            SUMX = np.nansum(X, axis=1)[:, None, :]
            SUMX2 = np.nansum(X2, axis=1)[:, None, :]
            COUNT = np.nansum(finit_tag, axis=1)[:, None, :]
            group_count = st2groupst(COUNT, daily_group, cross_sum)
            group_SUMX = st2groupst(SUMX, daily_group, cross_sum)
            group_mean = group_SUMX / group_count
            group_std = (group_count * st2groupst(SUMX2, daily_group, cross_sum) - group_mean ** 2) / group_count
            stk_std = (COUNT * SUMX2 - SUMX * SUMX) / COUNT ** 2
            return stk_std, group_std

        up_stk_std, up_group_std = get_group_std_and_stk_std(up_amt)
        down_stk_std, down_group_std = get_group_std_and_stk_std(down_amt)

        return arr_match_index((up_stk_std * up_group_std) / (down_stk_std * down_group_std), self.cal_date_range, self.date_range)

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
    cal_factor(numd={})
