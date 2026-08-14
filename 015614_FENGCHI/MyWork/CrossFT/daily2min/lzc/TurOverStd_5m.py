# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : TurOverStd_5m.py

import sys

sys.path.extend(['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/EnsembleMonitor',
                 '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python', '/data/user/015664/TriggeredTrading/StrongStockModel',
                 '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master',
                 '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic',
                 '/data/user/015664/TriggeredTrading'])

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class TurOverStd_5m(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 15
    author = 'lzc'
    logic = '当天日内5分钟换手率的波动*分组市值加权波动 昨日T时刻到当日T时刻为1天'
    article = ''
    freq = '5mins'
    basic_datas = {'daily': ['free_float_shares'], '30mins': [], '5mins': ['amt'], '1min': []}

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return self.database['5mins']['amt'], self.database['daily']['free_float_shares']

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        amt, free_float_shares = self.st_factor()

        import bottleneck
        def intrad_past_day_rolling_sum(x_, finit=None):
            shape = x_.shape
            if finit is None:
                finit = np.isfinite(x_)
            x = np.where(finit, x_, 0)
            return bottleneck.move_sum(np.concatenate([delay(x, 1), x], axis=1), window=shape[1], axis=1)[:, -shape[1]:, :]

        def intrad_past_day_rolling_std(x, finit=None):
            if finit is None:
                finit = np.isfinite(x)
            SUM = intrad_past_day_rolling_sum(x, finit)
            SUM2 = intrad_past_day_rolling_sum(x, finit)
            COUNT = intrad_past_day_rolling_sum(finit)
            return SUM2 / COUNT - (SUM / COUNT) ** 2

        free_float_shares = delay(free_float_shares, 1)
        stk_turnover = amt / free_float_shares  # (amt.swapaxes(0, 1) / free_float_shares[:, 0, :])
        daily_group = sameshape(free_float_shares, self.group_factor())
        minute_group = sameshape(amt, self.group_factor())
        stk_std = intrad_past_day_rolling_std(stk_turnover)  # [:, None, :]
        group_std = st2groupst(stk_std * free_float_shares, minute_group, cross_sum) / st2groupst(free_float_shares, daily_group, cross_sum)

        return arr_match_index(stk_std * group_std, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    # for group in groups:
    #     for func in funcs:
    #         print('-------------{}-----------{}-------------'.format(group,func))
    cal_factor()
    # send_message(['015664'],f'total calc time {time.time()-e}')
