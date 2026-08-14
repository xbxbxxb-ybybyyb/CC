# coding: utf-8
# Author：fengchi863
# Date ：2021/8/31 10:57

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class CloseVolCorrNor(crossFactor):
    cross_group = 'sw2'
    cross_func = 'cross_mean'
    extend_days = 10
    author = 'fc'
    freq = '1min'
    logic = '板块分钟量价五日均值除标准差'
    article = ''
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': ['close', 'vol']}

    def st_factor(self):
        close = self.database['1min']['close']
        vol = self.database['1min']['vol']
        return close, vol

    def calc_groupst(self):
        close, vol = self.st_factor()
        self.group = sameshape(close, self.group_factor())
        cum_corr = ts_cumcorr2(close, vol)
        tmp_ret = st2groupst(cum_corr, self.group, cross_mean)
        ret = tmp_ret  # dt_mean(tmp_ret, 5) / dt_std(tmp_ret, 5)
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    val1 = cal_factor(numd={})
    val2 = cal_factor(numd={'1min': 10})
    gap = abs(val1 - val2)
    print(np.nansum(gap))
