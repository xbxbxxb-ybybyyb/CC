# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File :RetWeightedVolRatio.py

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


class RetWeightedVolRatio(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = '自定义'
    extend_days = 15
    author = 'lzc'
    logic = '收益率加权成交额/总成交额   *  行业收益率加权成交额/总成交额'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['close'], '30mins': [], '5mins': ['amt', 'close'], '1min': []}

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return self.database['daily']['close'], self.database['5mins']['amt'], self.database['5mins']['close']

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        close, amt, close_min = self.st_factor()

        close_min = close_min.swapaxes(0, 1)
        amt = amt.swapaxes(0, 1)
        ret = close_min / delay(close_min) - 1

        weighted_sum_amt = np.nansum(amt * ret, axis=0)[:, None, :]
        sum_ret = np.nansum(ret, axis=0)[:, None, :]
        total_amt = np.nansum(amt, axis=0)[:, None, :]

        daily_group = sameshape(close, self.group_factor())

        group_val = st2groupst(weighted_sum_amt, daily_group, cross_sum) / st2groupst(sum_ret, daily_group, cross_sum) / st2groupst(total_amt, daily_group, cross_sum)
        stk_val = weighted_sum_amt / sum_ret / total_amt

        return arr_match_index(group_val * stk_val, self.cal_date_range, self.date_range)

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
    f = RetWeightedVolRatio()
    e = time.time()
    # f.result()
    f.save_result()
    print(f'total calc time {time.time() - e}')
    # send_message(['015664'],f'total calc time {time.time()-e}')
