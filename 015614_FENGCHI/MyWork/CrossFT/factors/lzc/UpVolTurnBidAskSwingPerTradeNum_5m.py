# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : UpVolTurnBidAskSwingPerTradeNum_5m.py

import sys

# sys.path.extend(['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/EnsembleMonitor', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python', '/data/user/015664/TriggeredTrading/StrongStockModel', '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master', '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic', '/data/user/015664/TriggeredTrading'])


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *
from basic.operators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class UpVolTurnBidAskSwingPerTradeNum_5m(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = '自定义'
    extend_days = 15
    author = 'lzc'
    logic = '放量bar买单均价和买单均价价差总和除与成交笔数 个股/分组 前日T时刻到当日T时刻为一日'
    article = ''
    freq = '5mins'
    basic_datas = {'daily': ['close', 'adjfactor'], '30mins': [], '5mins': ['amt', 'buytradeamt', 'selltradeamt', 'buytradevol', 'selltradevol', 'tradenum'], '1min': []}

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return [self.database['5mins'][x] for x in ['amt', 'buytradeamt', 'selltradeamt', 'buytradevol', 'selltradevol', 'tradenum']]

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        amt, buytradeamt, selltradeamt, buytradevol, selltradevol, trade_num = self.st_factor()
        minute_factor = sameshape(amt, self.group_factor())

        import bottleneck
        def intrad_past_day_rolling_sum(x_, finit=None):
            shape = x_.shape
            if finit is None:
                finit = np.isfinite(x_)
            x = np.where(finit, x_, 0)
            return bottleneck.move_sum(np.concatenate([delay(x, 1), x], axis=1), window=shape[1], axis=1)[:, -shape[1]:, :]

        buy_vwap = buytradeamt / buytradevol
        sell_vwap = selltradeamt / selltradevol
        diff = sell_vwap / buy_vwap - 1
        amt_pct_change = amt / delay(amt.swapaxes(0, 1)).swapaxes(0, 1) - 1
        up_diff = np.where(amt_pct_change > 0, diff, np.nan)
        up_trade_num = np.where(amt_pct_change > 0, trade_num, 0)

        rolling_sum_diff = intrad_past_day_rolling_sum(up_diff)
        rolling_sum_trade_num = intrad_past_day_rolling_sum(up_trade_num)

        stk_factor = rolling_sum_diff / rolling_sum_trade_num
        group_factor = st2groupst(rolling_sum_diff, minute_factor, cross_sum) / st2groupst(rolling_sum_trade_num, minute_factor, cross_sum)

        return arr_match_index(stk_factor * group_factor, self.cal_date_range, self.date_range)

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
    # send_message(['015664'],f'total calc time {time.time()-e}')
