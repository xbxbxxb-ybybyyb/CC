# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : BuySellPressureRollingSTD.py

import sys

# sys.path.extend(['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/EnsembleMonitor', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python', '/data/user/015664/TriggeredTrading/StrongStockModel', '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master', '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic', '/data/user/015664/TriggeredTrading'])


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class BuySellPressureRollingSTD_5m(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = '自定义'
    extend_days = 15
    author = 'lzc'
    logic = '个股买卖压日内波动率*行业买卖压波动率 昨日T时刻到当日T时刻为一日'
    article = ''
    freq = '5mins'
    basic_datas = {'daily': ['close'], '30mins': [], '5mins': ['buyorderamt', 'sellorderamt'], '1min': []}

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return self.database['daily']['close'], self.database['5mins']['buyorderamt'], self.database['5mins']['sellorderamt']

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        close, buyorderamt, sellorderamt = self.st_factor()

        minute_group = sameshape(buyorderamt, self.group_factor())

        group_buyorderamt = st2groupst(buyorderamt, minute_group, cross_sum)
        group_sellorderamt = st2groupst(sellorderamt, minute_group, cross_sum)

        stk_pressure = buyorderamt / sellorderamt
        group_pressure = group_buyorderamt / group_sellorderamt

        import bottleneck
        def intrad_past_day_rolling_sum(x):
            shape = x.shape
            # x = np.where(finit, x_)
            return bottleneck.move_sum(np.concatenate([delay(x, 1), x], axis=1), window=shape[1], axis=1)[:, -shape[1]:, :]

        def intrad_past_day_rolling_std(x, finit=None):
            if finit is None:
                finit = np.isfinite(x)
            SUM = intrad_past_day_rolling_sum(np.where(finit, x, 0))
            SUM2 = intrad_past_day_rolling_sum(np.where(finit, x ** 2, 0))
            COUNT = intrad_past_day_rolling_sum(finit)
            return (SUM2 / COUNT - (SUM / COUNT) ** 2) ** 0.5

        stk_std = intrad_past_day_rolling_std(stk_pressure)  # [:, None, :]
        group_std = intrad_past_day_rolling_std(group_pressure)

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
