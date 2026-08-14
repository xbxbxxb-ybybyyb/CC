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


class BCVPEwm5d(crossFactor):
    cross_group = 'sw2'
    cross_func = 'cross_mean'
    extend_days = 10
    start = 20140701
    # start = 20210525
    end = 20210531
    author = 'fc'
    freq = 'daily'
    logic = '个股收盘集合竞价阶段成交量占比按权重加权 - 组内集合竞价阶段成交量占比按权重加权'
    article = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': ['amt']}

    def st_factor(self):
        amt = self.database['1min']['amt']
        return amt

    def calc_groupst(self):
        amt = self.st_factor()
        amt1 = amt[:, [-1], :]
        amt2 = np.nansum(amt, axis=1, keepdims=True)
        call_auction_amt_pct = amt1 / amt2
        stk_ewm = self.dt_ewm(call_auction_amt_pct, 5)
        self.group = sameshape(amt1, self.group_factor())
        group_call_auction_amt_pct = st2groupst(amt1, self.group, cross_sum) / st2groupst(amt2, self.group, cross_sum)
        group_ewm = self.dt_ewm(group_call_auction_amt_pct, 5)
        ret = stk_ewm - group_ewm
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
    f = BCVPEwm5d()
    # print(f.result())
    f.save_result()
