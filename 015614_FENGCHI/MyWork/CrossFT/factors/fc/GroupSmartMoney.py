# coding: utf-8
# Author：fengchi863
# Date ：2021/12/14 16:06

from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.crossUtils import *
from basic.operators import *


class GroupSmartMoney(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 2
    author = 'fc'
    freq = '5mins'
    logic = '分组聪明钱因子，刻画每五分钟交易的聪明程度'
    article = '宽客学院 https://www.quantinfo.com/Article/View/735.html'
    basic_datas = {'daily': ['a_mkt_cap'], '30mins': [], '5mins': ['close_badj', 'volume'], '1min': []}

    def st_factor(self):
        close = self.database['5mins']['close_badj']
        vol = self.database['5mins']['volume']
        a_mkt_cap = self.database['daily']['a_mkt_cap']
        min_pct = dt_pct(close, 1)
        min_pct[:, :1, :] = np.nan
        return a_mkt_cap, min_pct, vol

    def calc_groupst(self):
        a_mkt_cap, min_pct, vol = self.st_factor()
        group = sameshape(min_pct, self.group_factor())
        group_pct = st2groupst(a_mkt_cap * min_pct, group, cross_mean)
        group_vol = st2groupst(vol, group, cross_sum)
        ret = abs(group_pct) / group_vol ** 0.5
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    # f = GroupSmartMoney(start=20210401, end=20210501)
    # print(f.result())

    cal_factor()
