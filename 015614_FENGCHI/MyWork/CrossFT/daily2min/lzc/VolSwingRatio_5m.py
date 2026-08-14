# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : VolSwingRatio_5m.py
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


class VolSwingRatio_5m(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = ''
    extend_days = 15
    author = 'lzc'
    logic = '个股尾部成交量振幅 * 行业调整后尾部成交量 前日T时刻到该日T时刻为一日'
    artical = ''
    freq = '5mins'
    basic_datas = {'daily': ['free_float_shares'], '30mins': [], '5mins': ['buytradevol', 'buytradeamt', 'selltradevol', 'selltradeamt', 'amt', 'vol'],
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
        volume, = [self.database['5mins'][x] for x in ['vol']]
        free_float_shares = delay(self.database['daily']['free_float_shares'], 1)
        minute_group = sameshape(volume, self.group_factor())

        import bottleneck
        def intrad_past_day_rolling_sum(x_, finit=None, window=None):
            shape = x_.shape
            if finit is None:
                finit = np.isfinite(x_)
            x = np.where(finit, x_, 0)
            return bottleneck.move_sum(np.concatenate([delay(x, 1), x], axis=1), window=shape[1] if window is None else window, axis=1)[:, -shape[1]:, :]


        adj_vol = volume / free_float_shares
        group_adj_vol = st2groupst(adj_vol, minute_group, cross_sum)

        tail_vol = intrad_past_day_rolling_sum(adj_vol, window=5)
        group_tail_vol = intrad_past_day_rolling_sum(group_adj_vol, window=5)

        total_vol = intrad_past_day_rolling_sum(adj_vol)
        group_total_vol = intrad_past_day_rolling_sum(group_adj_vol)  # [:, None, :]

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
    cal_factor()
    # send_message(['015664'],f'total calc time {time.time()-e}')
