# coding: utf-8
# Author：fengchi863
# Date ：2021/8/25 9:56

import talib

from basic.crossFactor import crossFactor
from basic.crossUtils import *


class ROC2h_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 5
    author = 'fc'
    freq = '5mins'
    logic = '个股2小时股价变动率行业内求均值'
    article = '渤海证券 20180710 – 行业轮动专题一'
    basic_datas = {'5mins': ['close_badj']}

    def st_factor(self):
        close = self.database['5mins']['close_badj']
        temp = close.reshape(-1, 1)
        roc = talib.ROC(temp[:, 0], timeperiod=24)
        roc = roc.reshape(len(self.cal_date_range), 48, -1)
        return roc

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    # f = ROC2h_5m(start=20210401, end=20210501)
    # print(f.result())
    cal_factor()
