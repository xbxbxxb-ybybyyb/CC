# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File :PerActiveTradeRetCorrWithVol.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class PerActiveTradeRetCorrWithVol(crossFactor):
    cross_group = 'sw1'
    cross_func = ''
    extend_days = 0
    author = 'lzc'
    logic = '开盘2小时每一块主动成交额(上行时主动买入成交额、下行时主动卖出成交额)推动的收益与成交量的相关系数'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['free_float_shares'], '30mins': [], '1min': [], '5mins': ['buytradeamt', 'selltradeamt', 'close', 'vol']}

    window = 15

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return [self.database['5mins'][x] for x in ['buytradeamt', 'selltradeamt', 'close', 'vol']]

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        buytradeamt, selltradeamt, close, vol = self.st_factor()
        free_float_shares = self.database['daily']['free_float_shares']
        daily = sameshape(free_float_shares, self.group_factor())
        # minute = sameshape(volume, self.group_factor())
        ret = close / delay(close.swapaxes(0, 1)).swapaxes(0, 1) - 1
        amt = np.where(ret > 0, buytradeamt, selltradeamt)
        Y = ret[:, :24, :] / amt[:, :24, :]
        X = vol[:, :24, :]

        count = np.isfinite(X) & np.isfinite(Y)
        X = np.where(count, X, 0)
        Y = np.where(count, Y, 0)

        SUMX2 = np.nansum(X ** 2, axis=1)[:, None, :]
        SUMY2 = np.nansum(Y ** 2, axis=1)[:, None, :]
        SUMXY = np.nansum(X * Y, axis=1)[:, None, :]
        SUMY = np.nansum(Y, axis=1)[:, None, :]
        SUMX = np.nansum(X, axis=1)[:, None, :]
        COUNT = np.nansum(count, axis=1)[:, None, :]

        stk_corr = (COUNT * SUMXY - SUMY * SUMX) / (COUNT * SUMX2 - SUMX ** 2) ** 0.5 / (COUNT * SUMY2 - SUMY ** 2) ** 0.5

        factor = st2groupst(stk_corr, daily, cross_mean) / st2groupst(stk_corr, daily, cross_std)

        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    # f = IntraCloseCorrWithVolRatio()
    # f.result()
    cal_factor(numd={})
