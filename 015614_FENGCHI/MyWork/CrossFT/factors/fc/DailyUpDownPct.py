# coding: utf-8
# Author：fengchi863
# Date ：2021/9/1 10:49

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class DailyUpDownPct(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 5
    author = 'fc'
    freq = 'daily'
    logic = '板块内个股日内上涨分钟与下降分钟bar的数量的比值'
    article = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': ['close']}

    def st_factor(self):
        close = self.database['1min']['close']
        pct = dt_pct(close, 1) > 0
        pct_up = np.nansum(pct, 1)
        pct_down = np.nansum(~pct, 1)
        return pct_up / pct_down

    def calc_groupst(self):
        ret = self.st_factor()
        self.group = sameshape(ret, self.group_factor())
        ret = st2groupst(ret, self.group, cross_mean)
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    # f = DailyUpDownPct(start=20210401, end=20210501)
    # print(f.result())
    # f.save_result()

    val = cal_factor('/data/user/015614/MyWork/CrossFT/factors/fc', 'DailyUpDownPct.py', {'daily': 6},
                     notrun=False)
