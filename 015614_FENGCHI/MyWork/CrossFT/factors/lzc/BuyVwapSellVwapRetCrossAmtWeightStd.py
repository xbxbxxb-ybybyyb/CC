# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : BuyVwapSellVwapRetCrossAmtWeightStd.py
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


class BuyVwapSellVwapRetCrossAmtWeightStd(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = ''
    extend_days = 15
    author = 'lzc'
    logic = '卖单VWAP对买单VWAP收益率在分组内用成交额面板上加权获得分组分钟面板加权收益 * 个股日内加权收益'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['free_float_shares'], '30mins': [], '5mins': ['buytradevol', 'buytradeamt', 'selltradevol', 'selltradeamt'], '1min': []}

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
        buytradevol, buytradeamt, selltradevol, selltradeamt = [self.database['5mins'][x] for x in ['buytradevol', 'buytradeamt', 'selltradevol', 'selltradeamt']]
        free_float_shares = self.database['daily']['free_float_shares']
        daily_group = sameshape(free_float_shares, self.group_factor())
        minute_group = sameshape(buytradevol, self.group_factor())

        buy_vwap, sell_vwap = buytradeamt / buytradevol, selltradeamt / selltradevol

        ret = sell_vwap / buy_vwap - 1
        total_amt = buytradeamt + selltradeamt

        adj_ret = ret * total_amt

        daily_adj_sum_ret = np.nansum(adj_ret, axis=1)[:, None, :]
        amt_sum = np.nansum(total_amt, axis=1)[:, None, :]

        daily_groupamt_sum = st2groupst(amt_sum, daily_group, cross_sum)
        daily_group_adj_sum_ret = st2groupst(daily_adj_sum_ret, daily_group, cross_sum)

        group_weighted_ret = daily_group_adj_sum_ret / daily_groupamt_sum

        stk_weighted_ret = daily_adj_sum_ret / amt_sum

        return arr_match_index(group_weighted_ret * stk_weighted_ret, self.cal_date_range, self.date_range)

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
    f = BuyVwapSellVwapRetCrossAmtWeightStd()
    e = time.time()
    # f.result()
    f.save_result()
    print(f'total calc time {time.time() - e}')
    # send_message(['015664'],f'total calc time {time.time()-e}')
