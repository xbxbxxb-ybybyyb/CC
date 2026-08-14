# coding: utf-8
# Author：fengchi863
# Date ：2021/9/10 11:05

from BombStockStrategy.Factor.basic.crossFactor import crossFactor
from CrossFT.basic.crossUtils import *
from CrossFT.basic.operators import *
from BombStockStrategy.conf.path_conf import factor_path


class CloseStd10d(crossFactor):
    extend_days = 10
    author = 'fc'
    start = 20140701
    # start = 20210401
    end = 20210531
    logic = '前10日收盘价的波动率'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['close_badj']}

    def st_factor(self):
        close_badj = self.database['daily']['close_badj']
        return close_badj

    def cal_factor(self):
        close_badj = self.st_factor()
        ret = dt_std(close_badj, 10)
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.cal_factor()


if __name__ == '__main__':
    f = CloseStd10d()
    f.check_factor(f.result())
    f.save_result()