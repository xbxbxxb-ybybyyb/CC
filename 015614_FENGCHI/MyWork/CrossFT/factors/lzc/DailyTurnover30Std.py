# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File :DailyTurnover30Std.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class DailyTurnover30Std(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 31
    author = 'lzc'
    logic = '日换手率近30日个股波动率*分组面板波动率'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['free_float_shares', 'close', 'amt'], '30mins': [], '5mins': [], '1min': []}

    window = 15

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return [self.database['daily'][x] for x in ['free_float_shares', 'close', 'amt']]

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        free_float_shares, close, amt = self.st_factor()
        daily_group = sameshape(free_float_shares, self.group_factor())
        turnover = free_float_shares / amt
        turnover_panel = (turnover,)
        for i in range(1, 30):
            turnover_panel = (delay(turnover, 1),) + turnover_panel
        turnover_panel = np.concatenate(turnover_panel, axis=1)

        finit_tag = np.isfinite(turnover_panel)
        X = np.where(finit_tag, turnover_panel, 0)
        X2 = X ** 2

        SUMX = np.nansum(X, axis=1)[:, None, :]
        SUMX2 = np.nansum(X2, axis=1)[:, None, :]
        COUNT = np.nansum(finit_tag, axis=1)[:, None, :]

        group_std = (st2groupst(SUMX2, daily_group, cross_sum) - st2groupst(SUMX, daily_group, cross_sum) ** 2) / st2groupst(COUNT, daily_group, cross_sum)
        stk_std = (SUMX2 - SUMX ** 2) / COUNT

        return arr_match_index(group_std * stk_std, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    # f = DailyTurnover30Std()
    # f.result()
    cal_factor(numd={})
