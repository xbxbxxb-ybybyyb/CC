# coding: utf-8
# Author：fengchi863
# Date ：2021/8/25 10:43

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *


class CYBZUpVwapTimePct(crossFactor):
    cross_group = None
    cross_func = None
    extend_days = 0
    author = 'fc'
    factor_name = 'CYBZUpVwapTimePct'
    freq = '1min'
    logic = '创业板指日内在均线上方的比例'
    article = '市场监控结论'
    basic_datas = {'1min': ['close_CYBZ']}

    def st_factor(self):
        close = self.database['1min']['close_CYBZ']
        ma = ts_cummean(close)
        time_flag = (close > ma)
        time_pct = ts_cumsum(time_flag) / np.arange(1, time_flag.shape[1] + 1)[None, :, None]
        time_pct = index2st(time_pct, len(self.code_list))
        return time_pct

    def result(self):
        return self.st_factor()


if __name__ == '__main__':
    # f = CYBZUpVwapTimePct(start=20210401, end=20210501)
    # print(f.result())
    cal_factor()
