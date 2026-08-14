# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : BarlySwingPerDealKurt_5m.py

import sys

# sys.path.extend(['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/EnsembleMonitor', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python', '/data/user/015664/TriggeredTrading/StrongStockModel', '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master', '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic', '/data/user/015664/TriggeredTrading'])


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *
from basic.operators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class BarlySwingPerDealKurt_5m(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = '自定义'
    extend_days = 15
    author = 'lzc'
    logic = '最近240分钟 分钟振幅总和除以成交笔数 个股因子*分组因子'
    article = ''
    freq = '5mins'
    basic_datas = {'daily': ['close', 'adjfactor'], '30mins': [], '5mins': ['amt', 'close', 'high', 'low', 'tradenum'], '1min': []}

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return [self.database['daily']['close']] + [self.database['5mins'][x] for x in ['amt', 'close', 'high', 'low', 'tradenum']]

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        close_daily, amt, close_min, high, low, tradenum = self.st_factor()
        adjfactor = self.database['daily']['adjfactor']
        minute_group = sameshape(tradenum, self.group_factor())
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
            group_count = st2groupst(COUNT, minute_group, cross_sum)
            group_EX3 = st2groupst(SUMX3, minute_group, cross_sum)
            group_SUMX = st2groupst(SUMX, minute_group, cross_sum)
            group_mean = group_SUMX / group_count
            group_std = (group_count * st2groupst(SUMX2, minute_group, cross_sum) - group_mean ** 2) / group_count ** 2

            stk_mean = SUMX / COUNT
            stk_EX3 = SUMX3 / COUNT
            stk_std = (COUNT * SUMX2 - SUMX * SUMX) / COUNT ** 2

            stk_skew = (stk_EX3 - 3 * stk_mean * stk_std - stk_mean ** 3) / stk_std ** 0.5
            group_skew = (group_EX3 - 3 * group_mean * group_std - group_mean ** 3) / group_std ** 1.5
            return stk_skew, group_skew

        adjusted_high = high * adjfactor / delay(close_daily * adjfactor, 1)
        adjusted_low = low * adjfactor / delay(close_daily * adjfactor, 1)

        barly_swing = adjusted_high - adjusted_low
        stk_skew, group_skew = get_group_std_and_stk_std(barly_swing)

        return arr_match_index(stk_skew * group_skew, self.cal_date_range, self.date_range)

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
