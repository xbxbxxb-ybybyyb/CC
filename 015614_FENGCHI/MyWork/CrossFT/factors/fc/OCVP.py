# coding: utf-8
# Author：fengchi863
# Date ：2021/9/14 14:57

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class OCVP(crossFactor):
    cross_group = 'sw2'
    cross_func = 'cross_mean'
    extend_days = 1

    author = 'fc'
    freq = '1min'
    logic = '个股开盘集合竞价阶段成交量相对于昨日集合竞价的比值'
    article = ''
    basic_datas = {'daily': [], '30min': [], '5min': [], '1min': ['amt']}

    def st_factor(self):
        amt = self.database['1min']['amt']
        yes_amt = ds_delay(amt, 1)
        call_auction_amt_pct = amt[:, 0, :] / yes_amt[:, 0, :]
        return amt, call_auction_amt_pct

    def calc_groupst(self):
        amt, call_auction_amt_pct = self.st_factor()
        self.group = sameshape(amt, self.group_factor())
        ret = np.repeat(call_auction_amt_pct[:, None], 242, axis=1)
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    # f = OCVP()
    # print(f.result())
    # f.save_result()

    cal_factor()
