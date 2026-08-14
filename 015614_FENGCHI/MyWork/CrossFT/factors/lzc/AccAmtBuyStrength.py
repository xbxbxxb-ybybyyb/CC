# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : AccAmtBuyStrength_5m.py

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


class AccAmtBuyStrength(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = '自定义'
    extend_days = 15
    author = 'lzc'
    logic = '按照挂单档位加权委买卖额差异的强度sharpe'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['close'], '30mins': [], '5mins': ['activesellorderamt', 'activebuyorderamt'], '1min': []}

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return self.database['daily']['close'], self.database['5mins']['activebuyorderamt'], self.database['5mins']['activesellorderamt']

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        close, activebuyorderamt, activesellorderamt = self.st_factor()

        minute_group = sameshape(activebuyorderamt, self.group_factor())

        group_buyorderamt = st2groupst(activebuyorderamt, minute_group,  self.group_func())
        group_sellorderamt = st2groupst(activesellorderamt, minute_group,  self.group_func())

        stk_diff = activebuyorderamt - activesellorderamt
        group_diff = group_buyorderamt - group_sellorderamt

        return arr_match_index(np.nanmean(stk_diff, axis=1)[:, None, :] / np.nanstd(group_diff, axis=1)[:, None, :], self.cal_date_range, self.date_range)

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
