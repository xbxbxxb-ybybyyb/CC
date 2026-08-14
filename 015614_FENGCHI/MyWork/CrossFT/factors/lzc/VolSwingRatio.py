# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : VolSwingRatio.py
import sys

sys.path.extend(['/data/user/015614/MyWork', '/data/user/015614/MyWork/StrongStockModel', '/data/user/015614/MyWork/StrongStockModel/System', '/data/user/015614/MyWork/LimitUpPredStrategy', '/data/user/015614/MyWork/FaaMonitor', '/data/user/015614/MyWork/R2D2', '/data/user/015614/MyWork/CrossFT', '/data/user/015614/MyWork/CrossFT/basic', '/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211207定增上趋势股测试', '/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211214测试趋势股卖出条件', '/data/user/015614/MyWork/SimiStock', '/data/user/015614/MyWork/GitProject/Factor', '/data/user/015614/MyWork/GitProject', '/data/user/015614/MyWork/GitProject/Riskfolio-Lib', '/data/user/015614/MyWork/GitProject/Riskfolio-Lib/riskfolio', '/data/user/015614/MyWork/SimiStock/dataApi', '/data/user/015614/MyWork/ensemblemonitor-strategy-python', '/data/user/015614/MyWork/MillenniumFalcon', '/data/user/015614/MyWork'])

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


class VolSwingRatio(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = ''
    extend_days = 15
    author = 'lzc'
    logic = '个股尾部成交量振幅 * 行业调整后尾部成交量'
    artical = ''
    freq = 'daily'
    basic_datas = {'daily': ['free_float_shares'], '30mins': [], '5mins': ['buytradevol', 'buytradeamt', 'selltradevol', 'selltradeamt', 'amt', 'volume'],
                   '1min': []}

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return  self.database['5mins']['close_badj']

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        volume, = [self.database['5mins'][x] for x in ['volume']]
        free_float_shares = self.database['daily']['free_float_shares']
        minute_group = sameshape(volume, self.group_factor())

        adj_vol = volume / free_float_shares
        group_adj_vol = st2groupst(adj_vol, minute_group, cross_sum)

        tail_vol = np.nansum(adj_vol[:, -5:, :], axis=1)[:, None, :]
        group_tail_vol = np.nansum(group_adj_vol[:, -5:, :], axis=1)[:, None, :]

        total_vol = np.nansum(adj_vol, axis=1)[:, None, :]
        group_total_vol = np.nansum(group_adj_vol, axis=1)[:, None, :]

        return arr_match_index(group_tail_vol * tail_vol / total_vol / group_total_vol, self.cal_date_range, self.date_range)

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
    f = VolSwingRatio()
    e = time.time()
    # f.result()
    f.result()
    print(f'total calc time {time.time() - e}')
    # send_message(['015664'],f'total calc time {time.time()-e}')
