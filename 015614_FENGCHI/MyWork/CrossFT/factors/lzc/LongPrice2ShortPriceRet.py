# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : LongPrice2ShortPriceRet.py
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
import gc


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class LongPrice2ShortPriceRet(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = ''
    extend_days = 15
    author = 'lzc'
    logic = '每个分钟上看多挂单均价(新增主动委买+新增被动委卖)的均价与每分钟上空力量(新增被动委买+新增主动委卖)挂单均价收益 个人股与分组复利 '
    article = ''
    freq = '5mins'
    basic_datas = {'daily': ['free_float_shares'], '30mins': [], '5mins': ['passivesellorderamt', 'activesellorderamt', 'passivesellordervol', 'activesellordervol',
                                                                           'passivebuyorderamt', 'activebuyorderamt', 'passivebuyordervol', 'activebuyordervol'], '1min': []}

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return  # self.database['5mins']['close_badj']

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        passivesellorderamt, activesellorderamt, passivesellordervol, activesellordervol, \
        passivebuyorderamt, activebuyorderamt, passivebuyordervol, activebuyordervol = [self.database['5mins'][x] for x in
                                                                                        ['passivesellorderamt', 'activesellorderamt', 'passivesellordervol', 'activesellordervol',
                                                                                         'passivebuyorderamt', 'activebuyorderamt', 'passivebuyordervol', 'activebuyordervol']]
        free_float_shares = self.database['daily']['free_float_shares']
        free_float_shares = delay(free_float_shares, 1)
        daily_group = sameshape(free_float_shares, self.group_factor())
        minute_group = sameshape(passivesellorderamt, self.group_factor())

        long_amt = activebuyorderamt + passivesellorderamt
        long_vol = activebuyordervol + passivesellordervol

        short_amt = activesellorderamt + passivebuyorderamt
        short_vol = activesellordervol + passivebuyordervol

        stk_pressure_net = (long_amt / long_vol) / (short_amt / short_vol)
        group_long_price = st2groupst(long_amt, minute_group, cross_sum) / st2groupst(long_vol, minute_group, cross_sum)
        group_short_price = st2groupst(short_amt, minute_group, cross_sum) / st2groupst(short_vol, minute_group, cross_sum)
        group_pressure_net = group_long_price / group_short_price
        factor = group_pressure_net * stk_pressure_net - 1

        return arr_match_index(factor, self.cal_date_range, self.date_range)

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
    f = LongPrice2ShortPriceRet()
    e = time.time()
    # f.result()
    f.result()
    print(f'total calc time {time.time() - e}')
    # send_message(['015664'],f'total calc time {time.time()-e}')
