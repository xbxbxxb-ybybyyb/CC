# coding: utf-8
# Author：fengchi863
# Date ：2021/11/3 14:00


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


class CallAuctionQRR(crossFactor):
    cross_group = 'sw2'
    cross_func = 'cross_mean'
    extend_days = 12
    author = 'fc'
    freq = '1min'
    logic = '个股开盘集合竞价阶段成交额相对于前10日成交额的均值的量比'
    article = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': ['amt']}

    def st_factor(self):
        amt = self.database['1min']['amt']
        return amt

    def calc_groupst(self):
        amt = self.st_factor()
        amt1 = amt[:, [0], :]
        amt_mean = dt_mean(_fill(amt1[:-1, :, :], 1), 10)
        call_auction_qrr = amt1 / amt_mean
        self.group = sameshape(amt1, self.group_factor())
        group_call_auction_amt_qrr = st2groupst(call_auction_qrr, self.group, cross_mean)
        group_call_auction_amt_qrr = np.repeat(group_call_auction_amt_qrr, 242, axis=1)
        ret = arr_match_index(group_call_auction_amt_qrr, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    # f = CallAuctionQRR(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()
