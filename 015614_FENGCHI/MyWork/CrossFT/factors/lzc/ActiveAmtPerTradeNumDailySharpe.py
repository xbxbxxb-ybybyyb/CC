# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : ActiveAmtPerTradeNumDailySharpe.py

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


class ActiveAmtPerTradeNumDailySharpe(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = '自定义'
    extend_days = 15
    author = 'lzc'
    logic = '平均每笔成交带来的新增主动委托量'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['a_mkt_cap'], '30mins': [], '5mins': ['activesellorderamt', 'activebuyorderamt', 'tradenum'], '1min': []}

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return self.database['daily']['a_mkt_cap'], self.database['5mins']['activebuyorderamt'], \
               self.database['5mins']['activesellorderamt'], self.database['5mins']['tradenum']

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        a_mkt_cap, activebuyorderamt, activesellorderamt, tradenum = self.st_factor()
        a_mkt_cap = delay(a_mkt_cap, 1)
        activeamt_ratio = (activebuyorderamt + activesellorderamt) / a_mkt_cap
        daily_group = sameshape(a_mkt_cap, self.group_factor())
        minute_group = sameshape(activebuyorderamt, self.group_factor())

        group_active_amt_ratio = st2groupst((activebuyorderamt + activesellorderamt), minute_group, cross_sum) / st2groupst(a_mkt_cap, daily_group, cross_sum)

        stk_factor = activeamt_ratio / tradenum
        group_factor = group_active_amt_ratio / st2groupst(tradenum, minute_group, cross_sum)
        factor = np.nanmean(stk_factor, axis=1) * np.nanmean(group_factor, axis=1) / np.nanstd(stk_factor, axis=1) / np.nanstd(group_factor, axis=1)

        return arr_match_index(factor[:, None, :], self.cal_date_range, self.date_range)

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
