# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : ActiveVwapCorrWithActiveAmtRatio_5m.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *
import bottleneck

def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1, axis=0):
    if axis == 0:
        return fill_nan(arr[:-l], l)
    else:
        return fill_nan(arr.swapaxes(0, axis)[:-l], l).swapaxes(0, axis)


class ActiveVwapCorrWithActiveAmtRatio_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 2
    author = 'lzc'
    logic = '主买成交VWAP与主买成交占比的相关系数 *分组因子值   按昨日 T时刻到今日T时刻为一日计算'
    article = ''
    freq = '5mins'
    basic_datas = {'daily': ['free_float_shares'], '30mins': [], '5mins': ['buytradeamt', 'buytradevol', 'vol'], '1min': []}

    window = 15

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return [self.database['5mins'][x] for x in ['buytradeamt', 'buytradevol', 'vol']]

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        buytradeamt, buytradevol, vol = self.st_factor()
        free_float_shares = self.database['daily']['free_float_shares']
        minute_factor = sameshape(buytradeamt, self.group_factor())
        # minute = sameshape(volume, self.group_factor())
        buytrade_vwap = buytradeamt / buytradevol
        shape = buytradevol.shape
        Y = buytradevol / vol
        X = buytrade_vwap / buytrade_vwap[:, [0], :]
        Y = np.concatenate([delay(Y, 1), Y], axis=1)
        X = np.concatenate([delay(X, 1), X], axis=1)

        count = np.isfinite(X) & np.isfinite(Y)
        X = np.where(count, X, 0)
        Y = np.where(count, Y, 0)

        SUMX2 = bottleneck.move_sum(X ** 2, window=shape[1], axis=1)[:, -shape[1]:, :]
        SUMY2 = bottleneck.move_sum(Y ** 2, window=shape[1], axis=1)[:, -shape[1]:, :]
        SUMXY = bottleneck.move_sum(X * Y, window=shape[1], axis=1)[:, -shape[1]:, :]
        SUMY = bottleneck.move_sum(Y, window=shape[1], axis=1)[:, -shape[1]:, :]
        SUMX = bottleneck.move_sum(X, window=shape[1], axis=1)[:, -shape[1]:, :]
        COUNT = bottleneck.move_sum(count, window=shape[1], axis=1)[:, -shape[1]:, :]

        stk_corr = (COUNT * SUMXY - SUMY * SUMX) / (COUNT * SUMX2 - SUMX ** 2) ** 0.5 / (COUNT * SUMY2 - SUMY ** 2) ** 0.5

        group_COUNT = st2groupst(COUNT, minute_factor, cross_sum)
        group_SUMX2 = st2groupst(SUMX2, minute_factor, cross_sum)
        group_SUMY2 = st2groupst(SUMY2, minute_factor, cross_sum)
        group_SUMXY = st2groupst(SUMXY, minute_factor, cross_sum)
        group_SUMY = st2groupst(SUMY, minute_factor, cross_sum)
        group_SUMX = st2groupst(SUMX, minute_factor, cross_sum)

        group_corr = (group_COUNT * group_SUMXY - group_SUMY * group_SUMX) / (group_COUNT * group_SUMX2 - group_SUMX ** 2) ** 0.5 / (
                group_COUNT * group_SUMY2 - group_SUMY ** 2) ** 0.5

        return arr_match_index(stk_corr * group_corr, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    # f = ActiveVwapCorrWithActiveAmtRatio()
    # f.result()
    cal_factor(numd={})
