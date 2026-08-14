# coding: utf-8
# Author：fengchi863
# Date ：2021/10/13 13:47

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class NormalCloseAmtCorrDecay(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 10
    author = 'fc'
    freq = 'daily'
    logic = '每日正常时间(amt在两倍标准差以内的时候)的量价相关性，衡量炒作情绪，组内取均值'
    article = ''
    basic_datas = {'daily': [], '30min': [], '5min': [], '1min': ['close', 'amt']}

    def st_factor(self):
        amt = self.database['1min']['amt']
        close = self.database['1min']['close']
        mean_amt = np.nanmean(amt, axis=1, keepdims=True)
        std_amt = np.nanstd(amt, axis=1, keepdims=True)
        amt_flag = amt > (mean_amt + 2 * std_amt)
        amt[amt_flag] = np.nan
        close[amt_flag] = np.nan

        EX = np.nanmean(amt, axis=1)
        EY = np.nanmean(close, axis=1)
        EXY = np.nanmean(amt * close, axis=1)
        STDX = np.nanstd(amt, axis=1)
        STDY = np.nanstd(close, axis=1)
        corr = (EXY - EX * EY) / (STDX * STDY)
        return corr

    def cal_groupst(self):
        corr = self.st_factor()
        group = sameshape(corr, self.group_factor())
        ret = st2groupst(corr, group, cross_mean)
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    # f = NormalCloseAmtCorrDecay(start=20210401, end=20210501)
    # print(f.result())

    val = cal_factor('/data/user/015614/MyWork/CrossFT/factors/fc', 'NormalCloseAmtCorrDecay.py', {'daily': 6}, notrun=False)
