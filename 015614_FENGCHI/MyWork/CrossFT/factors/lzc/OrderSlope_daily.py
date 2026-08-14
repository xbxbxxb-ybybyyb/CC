# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : OrderSlope_daily.py
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


def calc_ofi(adj_buytradevol, adj_selltradevol, vwap_buy, vwap_sell):
    vwap_buy_delay = delay(vwap_buy.swapaxes(0, 1), 1).swapaxes(0, 1)
    adj_selltradevol_delay = delay(adj_selltradevol.swapaxes(0, 1), 1).swapaxes(0, 1)
    vwap_sell_delay = delay(vwap_sell.swapaxes(0, 1), 1).swapaxes(0, 1)
    adj_buytradevol_delay = delay(adj_buytradevol.swapaxes(0, 1), 1).swapaxes(0, 1)

    delta_v_b = np.where(vwap_buy > vwap_buy_delay, adj_buytradevol, -1 * adj_buytradevol_delay)
    delta_v_b = np.where(vwap_buy == vwap_buy_delay, adj_buytradevol - adj_buytradevol_delay, delta_v_b)

    delta_v_a = np.where(vwap_sell > vwap_sell_delay, adj_selltradevol, -1 * adj_selltradevol_delay)
    delta_v_a = np.where(vwap_sell == vwap_sell_delay, adj_selltradevol - adj_selltradevol_delay, delta_v_a)
    return delta_v_b - delta_v_a


class OrderSlope_daily(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = ''
    extend_days = 15
    author = 'lzc'
    logic = '计算根据流通股票本折算订单失衡因子 再计算行业整体的订单失衡'
    artical = '中信建投	20210707	因子深度研究系列	多层次订单失衡及订单斜率因子'
    freq = 'daily'
    basic_datas = {'daily': ['free_float_shares'], '30mins': [], '5mins': ['buytradevol', 'buytradeamt', 'selltradevol', 'selltradeamt', 'close'], '1min': []}

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
        buytradevol, buytradeamt, selltradevol, selltradeamt, close = [self.database['5mins'][x] for x in ['buytradevol', 'buytradeamt', 'selltradevol', 'selltradeamt', 'close']]
        free_float_shares = self.database['daily']['free_float_shares']
        adj_buytradevol = buytradevol / free_float_shares
        adj_selltradevol = selltradevol / free_float_shares
        vwap_buy = buytradeamt / buytradevol
        vwap_sell = selltradeamt / selltradevol

        stk_slope = (np.log(vwap_sell) - np.log(vwap_buy)) / (np.log(adj_buytradevol) + np.log(adj_selltradevol))

        minute_group = sameshape(buytradevol, self.group_factor())
        group_buyvwap = st2groupst(buytradeamt, minute_group, cross_sum) / st2groupst(buytradevol, minute_group, cross_sum)
        group_sell_vwap = st2groupst(selltradeamt, minute_group, cross_sum) / st2groupst(selltradevol, minute_group, cross_sum)
        group_adj_buyvol = st2groupst(adj_buytradevol, minute_group, cross_sum)
        group_adj_sellvol = st2groupst(adj_selltradevol, minute_group, cross_sum)
        group_slope = (np.log(group_sell_vwap) - np.log(group_buyvwap)) / (np.log(group_adj_buyvol) + np.log(group_adj_sellvol))

        return arr_match_index((np.nanmean(group_slope, axis=1) * np.nanmean(stk_slope, axis=1))[:, None, :], self.cal_date_range, self.date_range)

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
    f = OrderSlope_daily()
    e = time.time()
    # f.result()
    f.save_result()
    print(f'total calc time {time.time() - e}')
    # send_message(['015664'],f'total calc time {time.time()-e}')
