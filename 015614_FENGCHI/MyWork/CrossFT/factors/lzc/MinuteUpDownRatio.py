# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File :MinuteUpDownRatio.py

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


class MinuteUpDownRatio(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 15
    author = 'lzc'
    logic = '5分钟bar上超过或两倍标准差的bar的数量/小于-2被标准差的数量 * 组的该值'
    article = '中信建投	20200709	因子深度研究系列	高频量价选股因子初探'
    freq = 'daily'
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
        close, = [self.database['5mins'][x].swapaxes(0, 1) for x in ['close']]
        daily_group = sameshape(self.database['daily']['close'], self.group_factor())

        std = np.nanstd(close, axis=0)
        mean = np.nanmean(close, axis=0)
        import gc
        z_close = (close - mean) / std
        del mean, std
        gc.collect()

        over_2_std_count = np.nansum(np.where(z_close > 2, 1, 0), axis=0)[:, None, :]
        lower_neg2_std_count = np.nansum(np.where(z_close < -2, 1, 0), axis=0)[:, None, :]
        over_ratio = over_2_std_count / lower_neg2_std_count
        group_over_2_std_count = st2groupst(over_2_std_count, daily_group, cross_sum)
        group_neg2_std_count = st2groupst(lower_neg2_std_count, daily_group, cross_sum)

        group_ratio = group_over_2_std_count / group_neg2_std_count
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
    val1 = cal_factor(numd={})
    val2 = cal_factor(numd={'daily': 10})
    gap = abs(val1 - val2)
    print(np.sum(np.where(np.isfinite(gap), gap, 0)))
