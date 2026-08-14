# coding: utf-8
# Author：fengchi863
# Date ：2021/9/14 14:57

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


def _fill(arr, l, axis=0):
    if arr.ndim == 2:
        return np.pad(arr, ((l, 0), (0, 0)), mode='constant', constant_values=np.nan)

    elif arr.ndim == 3:
        if axis:
            return np.pad(arr, ((0, 0), (l, 0), (0, 0)), mode='constant', constant_values=np.nan)
        else:
            return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)

    else:
        raise ValueError


class BCVPEwm5d_5m(crossFactor):
    cross_group = 'sw2'
    cross_func = 'cross_mean'
    extend_days = 20
    author = 'fc'
    freq = '5mins'
    logic = '组内集合竞价阶段成交量占比按权重加权'
    article = ''
    basic_datas = {'5mins': ['amt']}

    def st_factor(self):
        amt = self.database['5mins']['amt']
        amt = ds_delay(amt, 1)
        return amt

    def calc_groupst(self):
        amt = self.st_factor()
        amt1 = amt[:, [-1], :]
        amt2 = np.nansum(amt, axis=1, keepdims=True)
        self.group = sameshape(amt1, self.group_factor())
        group_call_auction_amt_pct = st2groupst(amt1, self.group, cross_sum) / st2groupst(amt2, self.group, cross_sum)
        group_ewm = self.dt_ewm(group_call_auction_amt_pct, 5)
        ret = group_ewm
        ret = np.repeat(ret, 48, axis=1)
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()

    @staticmethod
    def dt_ewm(x, m2):
        x = x.copy()
        ar = ArrReshape()
        weight = np.array(list(map(lambda y: 1 / (y + 2), np.arange(m2).astype('float32')))[::-1])
        x = ar.to2d(x)
        xf = np.isfinite(x)
        x[~ xf] = 0
        cx = np.apply_along_axis(np.convolve, 0, x, weight, 'valid')
        cw = np.apply_along_axis(np.convolve, 0, xf, weight, 'valid')
        cn = bottleneck.move_sum(xf.astype('float32'), m2, axis=0)[m2 - 1:]
        cw[cn < m2 / 2] = np.nan
        return ar.to3d(_fill(cx / cw, m2 - 1))


if __name__ == '__main__':
    # f = BCVPEwm5d_5m(start=20210401, end=20210501)
    # print(f.result())
    cal_factor()
