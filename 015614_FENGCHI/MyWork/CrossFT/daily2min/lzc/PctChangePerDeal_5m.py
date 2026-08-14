# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File :PctChangePerDeal.py

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


class PctChangePerDeal_5m(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 15
    author = 'lzc'
    logic = '分钟bar涨跌幅/成交笔数  *  组内涨跌幅之和/组内成交笔数之和'
    article = '中信建投	20200709	因子深度研究系列	高频量价选股因子初探'
    freq = '5mins'
    basic_datas = {'daily': ['close', 'open'], '30mins': [], '5mins': ['numtrade', 'close'], '1min': []}

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
        numtrade, close = [self.database['5mins'][x] for x in ['numtrade', 'close']]
        # open_, close = [self.database['daily'][x] for x in ['close', 'open']]
        pct_change = close / delay(close.swapaxes(0, 1)).swapaxes(0, 1)
        # daily_trade_num = np.nansum(numtrade, axis=0)[:, None, :]

        per_deal = pct_change / numtrade

        group = sameshape(pct_change, self.group_factor())

        group_total_pct_change = st2groupst(pct_change, group, cross_sum)
        group_total_tradenum = st2groupst(numtrade, group, cross_sum)

        group_per_deal = group_total_pct_change / group_total_tradenum

        return arr_match_index(per_deal * group_per_deal, self.cal_date_range, self.date_range)

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
    # f = PctChangePerDeal()
    e = time.time()
    cal_factor()
    # f.result()
    # f.save_result()
    print(f'total calc time {time.time() - e}')
    # send_message(['015664'],f'total calc time {time.time()-e}')
