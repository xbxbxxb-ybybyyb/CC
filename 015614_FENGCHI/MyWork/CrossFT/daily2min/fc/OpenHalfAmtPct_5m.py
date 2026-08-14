# coding: utf-8
# Author：fengchi863
# Date ：2021/9/27 13:26

from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.crossUtils import *
from operators import *


class OpenHalfAmtPct_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 2
    author = 'fc'
    logic = '开盘前半小时行业成交量与昨日的比值占比'
    article = ''
    freq = '5mins'
    basic_datas = {'5mins': ['amt']}

    def st_factor(self):
        amt = self.database['5mins']['amt']
        yes_amt = ds_delay(amt, 1)
        return amt, yes_amt

    def cal_groupst(self):
        amt, yes_amt = self.st_factor()
        stgroup = sameshape(amt, self.group_factor())
        amt1000 = np.nansum(amt[:, :6, :], axis=1, keepdims=True)
        yes_amt1000 = np.nansum(yes_amt[:, :6, :], axis=1, keepdims=True)
        # amt = np.nansum(amt, axis=1, keepdims=True)
        amt_pct = st2groupst(amt1000, stgroup, cross_sum) / \
                  st2groupst(yes_amt1000, stgroup, cross_sum)
        ret = arr_match_index(amt_pct, self.cal_date_range, self.date_range)
        ret[:, :6, :] = np.nan  # 剔除未来信息
        return ret

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    f = OpenHalfAmtPct_5m(start=20210401, end=20210501)
    f.result()
    cal_factor()
