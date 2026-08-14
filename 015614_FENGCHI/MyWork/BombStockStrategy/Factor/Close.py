# coding: utf-8
# Author：fengchi863
# Date ：2021/9/10 14:14

'''
收盘价
'''

from BombStockStrategy.Factor.basic.crossFactor import crossFactor
from CrossFT.basic.crossUtils import *
from CrossFT.basic.operators import *
from BombStockStrategy.conf.path_conf import factor_path


class Close(crossFactor):
    extend_days = 0
    author = 'fc'
    start = 20140701
    # start = 20210401
    end = 20210531
    logic = '收盘价'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['close']}

    def st_factor(self):
        close = self.database['daily']['close']
        return close

    def cal_factor(self):
        close = self.st_factor()
        ret = arr_match_index(close, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.cal_factor()


if __name__ == '__main__':
    f = Close()
    f.check_factor(f.result())
    f.save_result()
