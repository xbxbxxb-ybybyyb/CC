# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : BuyVwapSellVwapRetActiveStd_5m.py
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


class BuyVwapSellVwapRetActiveStd_5m(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = ''
    extend_days = 15
    author = 'lzc'
    logic = '卖单VWAP对买单VWAP收益率对分组收益的超额收益的分组波动率 * 个股的超额收益  按昨日 T时刻到今日T时刻为一日计算'
    article = ''
    freq = '5mins'
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

        group_ret = st2groupst(ret * free_float_shares, minute_group, cross_sum) / st2groupst(free_float_shares, daily_group, cross_sum)
        active = ret - group_ret
        shape = ret.shape
        import bottleneck
        intrad_past_day_rolling_sum = lambda x: bottleneck.move_sum(np.concatenate([delay(x, 1), x], axis=1), window=shape[1], axis=1)[:, -shape[1]:, :]
        intrad_past_day_rolling_mean = lambda x: bottleneck.move_mean(np.concatenate([delay(x, 1), x], axis=1), window=shape[1], axis=1)[:, -shape[1]:, :]

        X_finit = np.isfinite(active)
        active = np.where(X_finit, active, 0)

        X = intrad_past_day_rolling_sum(active)
        X2 = intrad_past_day_rolling_sum(active ** 2)
        count = intrad_past_day_rolling_sum(X_finit)
        SUMX = st2groupst(X, minute_group, cross_sum)
        SUMX2 = st2groupst(X2, minute_group, cross_sum)
        COUNT = st2groupst(count, minute_group, cross_sum)
        group_std = (SUMX2 - SUMX ** 2) / COUNT

        return arr_match_index(intrad_past_day_rolling_mean(active) * group_std, self.cal_date_range, self.date_range)

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
    # f = BuyVwapSellVwapRetActiveStd()
    e = time.time()
    # f.result()
    cal_factor(numd={})

    # f.save_result()
    print(f'total calc time {time.time() - e}')
    # send_message(['015664'],f'total calc time {time.time()-e}')
