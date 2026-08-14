# coding: utf-8
# Author：fengchi863
# Date ：2021/11/15 10:20

from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.crossUtils import *
from basic.operators import *


class MinuteVolatilityPriceCorr(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 30
    author = 'fc'
    freq = 'daily'
    logic = '价格分钟线5分钟波动率与价格的相关性，相关性越低，说明异常炒作越少，具备较为稳定的超额能力'
    article = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': ['close_badj']}

    def st_factor(self):
        close = self.database['1min']['close_badj']
        close /= close[:, [0]]
        close_std = bottleneck.move_std(close, 5, 5, 1)
        # close_ = close.transpose(1, 2, 0)[None]
        # close_std[~ np.isfinite(close_std)] = np.nan
        close_std[:, :5, :] = np.nan
        close[:, :5, :] = np.nan

        n = np.isfinite(close) | np.isfinite(close_std)
        close[~ n] = 0
        close_std[~ n] = 0
        cx = close.sum(axis=1)
        cy = close_std.sum(axis=1)
        cx2 = (close ** 2).sum(axis=1)
        cy2 = (close_std ** 2).sum(axis=1)
        cxy = (close * close_std).sum(axis=1)
        cn = n.sum(axis=1)
        corr = (cxy - cx * cy / cn) / ((cx2 - cx ** 2 / cn) * (cy2 - cy ** 2 / cn)) ** 0.5
        corr[cn < 5] = np.nan
        # EX = np.nanmean(close_std, axis=1)
        # EY = np.nanmean(close, axis=1)
        # EXY = np.nanmean(close_std * close, axis=1)
        # STDX = np.nanstd(close_std, axis=1)
        # STDY = np.nanstd(close, axis=1)
        # corr = (EXY - EX * EY) / (STDX * STDY)
        # # corr[np.isnan(corr)] = 0
        # # corr[np.isinf(corr)] = 0
        corr = corr[:, None]
        return corr

    def calc_groupst(self):
        indicator = self.st_factor()
        group = sameshape(indicator, self.group_factor())
        group_ret = st2groupst(indicator, group,  self.group_func())
        ret = arr_match_index(group_ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    # f = MinuteVolatilityPriceCorr(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()
