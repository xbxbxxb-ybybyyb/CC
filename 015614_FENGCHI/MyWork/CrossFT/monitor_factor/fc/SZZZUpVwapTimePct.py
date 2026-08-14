# coding: utf-8
# Author：fengchi863
# Date ：2021/8/19 11:08

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *


class SZZZUpVwapTimePct(crossFactor):
    extend_days = 0
    author = 'fc'
    factor_name = 'SZZZUpVwapTimePct'
    freq = '1min'
    logic = '上证指数日内在均线上方的比例'
    basic_datas = {'1min': ['close_SZCZ']}

    def st_factor(self):
        close = self.database['1min']['close_SZCZ']
        ma = ts_cummean(close)
        time_flag = (close > ma)
        time_pct = ts_cumsum(time_flag) / np.arange(1, time_flag.shape[1] + 1)[None, :, None]
        time_pct = index2st(time_pct, len(self.code_list))
        return time_pct

    def result(self):
        return self.st_factor()


if __name__ == '__main__':
    cal_factor()
