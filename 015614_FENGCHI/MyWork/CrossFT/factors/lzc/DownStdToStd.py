# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File :DownStdToStd.py

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


class DownStdToStd(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 15
    author = 'lzc'
    logic = '个股下行波动率/波动率   *  分组收益均值下行波动率/波动率'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['close'], '30mins': [], '5mins': ['close_badj'], '1min': []}

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
        close, = [self.database['5mins'][x].swapaxes(0, 1) for x in ['close_badj']]
        # daily_group = sameshape(self.database['daily']['close'], self.group_factor())

        ret = (close / delay(close) - 1).swapaxes(0, 1)
        minute_group = sameshape(ret, self.group_factor())

        std = np.nanstd(ret, axis=1)[:, None, :]
        up_std = np.nanstd(np.where(ret < 0, ret, np.nan), axis=1)[:, None, :]

        group_mean_ret = st2groupst(ret, minute_group, cross_mean)

        group_std = np.nanstd(group_mean_ret, axis=1)[:, None, :]
        group_up_std = np.nanstd(np.where(group_mean_ret < 0, group_mean_ret, np.nan), axis=1)[:, None, :]

        return arr_match_index((up_std * group_up_std) / (group_std * std), self.cal_date_range, self.date_range)

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
    f = DownStdToStd()
    e = time.time()
    # f.result()
    f.save_result()
    print(f'total calc time {time.time() - e}')
    # send_message(['015664'],f'total calc time {time.time()-e}')
