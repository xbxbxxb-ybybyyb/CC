# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : GroupSelfCorr.py
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


class GroupSelfCorr(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 15
    author = 'lzc'
    logic = '个股收益在组内的zscore的自相关性'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': [], '30mins': [], '5mins': ['close_badj'], '1min': []}

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return self.database['5mins']['close_badj']

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        close_badj = self.st_factor()
        close_badj = close_badj.swapaxes(0, 1)
        ret = close_badj / delay(close_badj) - 1
        ret = ret.swapaxes(0, 1)
        self.group = sameshape(ret, self.group_factor())
        grou_zscore = (ret - st2groupst(ret, self.group, cross_mean)) / st2groupst(ret, self.group, cross_std)
        grou_zscore_lag = delay(grou_zscore.swapaxes(0, 1)).swapaxes(0, 1)

        EXY = np.nanmean(grou_zscore_lag * grou_zscore, axis=1)
        EXEY = np.nanmean(grou_zscore, axis=1) * np.nanmean(grou_zscore_lag, axis=1)
        STDXSTDY = np.nanstd(grou_zscore, axis=1) * np.nanstd(grou_zscore_lag, axis=1)

        corr = (EXY - EXEY) / STDXSTDY

        return arr_match_index(corr[:, None, :], self.cal_date_range, self.date_range)

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
    f = GroupSelfCorr()
    e = time.time()
    # f.result()
    f.save_result()
    print(f'total calc time {time.time() - e}')
    # send_message(['015664'],f'total calc time {time.time()-e}')
