# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : BuyVwapSellVwapRetStd_5m.py
import sys

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class BuyVwapSellVwapRetStd_5m(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 15
    author = 'lzc'
    logic = '卖单VWAP对买单VWAP收益率 个股日内波动率 * 分组日内波动率   按昨日 T时刻到今日T时刻为一日计算'
    article = ''
    freq = '5mins'
    basic_datas = {'daily': ['close'], '30mins': [], '5mins': ['buytradevol', 'buytradeamt', 'selltradevol', 'selltradeamt'], '1min': []}

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

        buy_vwap, sell_vwap = buytradeamt / buytradevol, selltradeamt / selltradevol

        ret = sell_vwap / buy_vwap - 1
        shape = buytradevol.shape
        import bottleneck
        intrad_past_day_rolling_sum = lambda x: bottleneck.move_sum(np.concatenate([delay(x, 1), x], axis=1), window=shape[1], axis=1)[:, -shape[1]:, :]

        def intrad_past_day_rolling_std(x, finit):
            SUM = intrad_past_day_rolling_sum(np.where(finit, x, 0))
            SUM2 = intrad_past_day_rolling_sum(np.where(finit, x ** 2, 0))
            COUNT = intrad_past_day_rolling_sum(finit)
            return SUM2 / COUNT - (SUM / COUNT) ** 2

        ret_finit = np.isfinite(ret)
        ret = np.where(ret_finit, ret, 0)
        stk_std = intrad_past_day_rolling_std(ret, ret_finit)  # [:, None, :]

        X = intrad_past_day_rolling_sum(ret)  # [:, None, :]
        X2 = intrad_past_day_rolling_sum(ret ** 2)
        count = intrad_past_day_rolling_sum(ret_finit)

        minute_group = sameshape(ret, self.group_factor())
        SUMX = st2groupst(X, minute_group, cross_sum)
        SUMX2 = st2groupst(X2, minute_group, cross_sum)
        COUNT = st2groupst(count, minute_group, cross_sum)

        group_std = (SUMX2 - SUMX ** 2) / COUNT

        return arr_match_index(group_std * stk_std, self.cal_date_range, self.date_range)

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
    # f = BuyVwapSellVwapRetStd()
    e = time.time()
    # f.result()
    # f.save_result()
    cal_factor()
    print(f'total calc time {time.time() - e}')
    # send_message(['015664'],f'total calc time {time.time()-e}')
