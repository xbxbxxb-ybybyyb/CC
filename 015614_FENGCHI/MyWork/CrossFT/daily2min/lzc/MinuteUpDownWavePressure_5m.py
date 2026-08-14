# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File :MinuteUpDownWavePressure_5m.py

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


class MinuteUpDownWavePressure_5m(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 15
    author = 'lzc'
    logic = '5分钟bar上超过或两倍标准差的振幅之和/小于-2被标准差的振幅之和 * 组的该值 前日T时刻到当日T时刻为一日'
    article = '中信建投	20200709	因子深度研究系列	高频量价选股因子初探'
    freq = '5mins'
    basic_datas = {'daily': ['close'], '30mins': [], '5mins': ['close'], '1min': []}

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return  # self.database['daily']['close_badj'], self.database['daily']['free_float_shares'], self.database['daily']['amt']

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        # high,low = [self.database['daily'][x] for x in ['high','low']]
        close, = [self.database['5mins'][x] for x in ['close']]
        daily_group = sameshape(close, self.group_factor())

        import bottleneck
        def intrad_past_day_rolling_sum(x):
            shape = x.shape
            # x = np.where(finit, x_)
            return bottleneck.move_sum(np.concatenate([delay(x, 1), x], axis=1), window=shape[1], axis=1)[:, -shape[1]:, :]

        def intrad_past_day_rolling_mean(x, finit=None):
            if finit is None:
                finit = np.isfinite(x)
            SUM = intrad_past_day_rolling_sum(np.where(finit, x, 0))
            COUNT = intrad_past_day_rolling_sum(finit)
            return SUM / COUNT

        def intrad_past_day_rolling_std(x, finit=None):
            if finit is None:
                finit = np.isfinite(x)
            SUM = intrad_past_day_rolling_sum(np.where(finit, x, 0))
            SUM2 = intrad_past_day_rolling_sum(np.where(finit, x ** 2, 0))
            COUNT = intrad_past_day_rolling_sum(finit)
            return SUM2 / COUNT - (SUM / COUNT) ** 2

        def intrad_past_day_rolling_mv(x, finit=None):
            if finit is None:
                finit = np.isfinite(x)
            SUM = intrad_past_day_rolling_sum(np.where(finit, x, 0))
            SUM2 = intrad_past_day_rolling_sum(np.where(finit, x ** 2, 0))
            COUNT = intrad_past_day_rolling_sum(finit)
            return SUM / COUNT, SUM2 / COUNT - (SUM / COUNT) ** 2

        mean, std = intrad_past_day_rolling_mv(close)

        import gc
        z_close = (close - mean) / std
        del mean, std
        gc.collect()

        over_2_std_wavecount = intrad_past_day_rolling_sum(np.where(z_close > 2, z_close, 0))  # , axis=0)[:, None, :]
        lower_neg2_std_wavecount = intrad_past_day_rolling_sum(np.where(z_close < -2, z_close, 0)) * -1  # , axis=0)[:, None, :] * -1
        over_ratio = over_2_std_wavecount / lower_neg2_std_wavecount
        group_over_2_std_wavecount = st2groupst(over_2_std_wavecount, daily_group, cross_sum)
        group_neg2_std_wavecount = st2groupst(lower_neg2_std_wavecount, daily_group, cross_sum)

        group_ratio = group_over_2_std_wavecount / group_neg2_std_wavecount
        factor = group_ratio * over_ratio
        factor[~np.isfinite(factor)] = np.nan
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    val1 = cal_factor()
    # val2 = cal_factor(numd={'daily': 10})
    # gap = abs(val1 - val2) / abs(val1)
    # print(np.nansum(gap))
