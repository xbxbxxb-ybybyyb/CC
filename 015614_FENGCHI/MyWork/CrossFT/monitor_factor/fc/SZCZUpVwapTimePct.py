# coding: utf-8
# Author：fengchi863
# Date ：2021/8/25 10:43

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *


class SZCZUpVwapTimePct(crossFactor):
    extend_days = 0
    author = 'fc'
    freq = '1min'
    logic = '深证成指日内在均线上方的比例'
    article = '市场监控结论'
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
    # f = SZCZUpVwapTimePct(start=20210401, end=20210501)
    # print(f.result())

    val = cal_factor(onlycheck=True)


