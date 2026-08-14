# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : UpBuytradeVwap2DownSellTradeVwapProfit_5m.py
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


class UpBuytradeVwap2DownSellTradeVwapProfit_5m(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = ''
    extend_days = 15
    author = 'lzc'
    logic = '截面上分组内上行日内主动买入均价对截面上下行主动卖出均价的收益率 与 个股该值复利 前一日T时刻到当日T时刻为一日'
    article = ''
    freq = '5mins'
    basic_datas = {'daily': ['free_float_shares'], '30mins': [], '5mins': ['buytradeamt', 'selltradeamt', 'buytradevol', 'selltradevol', 'close'], '1min': []}

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
        buytradeamt, selltradeamt, buytradevol, selltradevol, close = [self.database['5mins'][x] for x in ['buytradeamt', 'selltradeamt', 'buytradevol', 'selltradevol', 'close']]
        free_float_shares = self.database['daily']['free_float_shares']
        free_float_shares = delay(free_float_shares, 1)
        # daily_group = sameshape(free_float_shares, self.group_factor())
        minute_group = sameshape(buytradeamt, self.group_factor())

        ret = close / delay(close) - 1
        import bottleneck
        def intrad_past_day_rolling_sum(x, finit=None):
            x = x.copy()
            if finit is None:
                finit = np.isfinite(x)
            shape = x.shape
            x = np.where(finit, x, 0)
            return bottleneck.move_sum(np.concatenate([delay(x, 1), x], axis=1), window=shape[1], axis=1)[:, -shape[1]:, :]

        up = ret > 0
        down = ret < 0
        up_buy_tradeamt = intrad_past_day_rolling_sum(np.where(up, buytradeamt, 0), up)  # [:, None, :]
        up_buy_tradevol = intrad_past_day_rolling_sum(np.where(up, buytradevol, 0), up)  # [:, None, :]
        down_sell_tradeamt = intrad_past_day_rolling_sum(np.where(down, selltradeamt, 0), down)  # [:, None, :]
        down_sell_tradevol = intrad_past_day_rolling_sum(np.where(down, selltradevol, 0), down)  # [:, None, :]

        group_up_buy_tradeamt = st2groupst(up_buy_tradeamt, minute_group, cross_sum)
        group_up_buy_tradevol = st2groupst(up_buy_tradevol, minute_group, cross_sum)
        group_down_sell_tradeamt = st2groupst(down_sell_tradeamt, minute_group, cross_sum)
        group_down_sell_tradevol = st2groupst(down_sell_tradevol, minute_group, cross_sum)

        stk_cum_net = (up_buy_tradeamt / up_buy_tradevol) / (down_sell_tradeamt / down_sell_tradevol)
        group_cum_net = (group_up_buy_tradeamt / group_up_buy_tradevol) / (group_down_sell_tradeamt / group_down_sell_tradevol)
        factor = stk_cum_net * group_cum_net - 1

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
    cal_factor()
    # send_message(['015664'],f'total calc time {time.time()-e}')
