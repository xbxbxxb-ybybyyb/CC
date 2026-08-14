# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : LowestDPathiLIQUIDITY.py

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


class LowestDPathiLIQUIDITY(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 15
    author = 'lzc'
    logic = '最短路径/交易额表示最短路径非流动性，个股非流动性*分组非流动性'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['open', 'high', 'low', 'close', 'amt', 'free_float_shares'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return [self.database['daily'][x] for x in ['open', 'high', 'low', 'close', 'amt', 'free_float_shares']]

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        cell = self.st_factor()
        open_, high, low, close, amt, free_float_shares = cell
        lowest_path = 2 * (high - low) / abs(open_ - close)
        stk_illiquidity = lowest_path / amt
        daily_group = sameshape(free_float_shares, self.group_factor())
        group_illiquidity = lowest_path * free_float_shares / st2groupst(free_float_shares, daily_group, cross_sum)

        return arr_match_index(stk_illiquidity * group_illiquidity, self.cal_date_range, self.date_range)

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
    f = LowestDPathiLIQUIDITY()
    e = time.time()
    # f.result()
    f.save_result()
    print(f'total calc time {time.time() - e}')
    # send_message(['015664'],f'total calc time {time.time()-e}')
