# coding: utf-8
# Author：fengchi863
# Date ：2021/9/9 20:20

from BombStockStrategy.Factor.basic.crossFactor import crossFactor
from CrossFT.basic.crossUtils import *
from CrossFT.basic.operators import *
from BombStockStrategy.conf.path_conf import factor_path


class UpperShadowPct(crossFactor):
    extend_days = 10
    author = 'fc'
    start = 20140701
    # start = 20210401
    end = 20210531
    logic = '上影线比例'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['close_badj', 'high_badj', 'low_badj']}

    def st_factor(self):
        close_badj = self.database['daily']['close_badj']
        high_badj = self.database['daily']['high_badj']
        low_badj = self.database['daily']['low_badj']
        ret = (high_badj - close_badj) / (high_badj - low_badj)
        return ret

    def result(self):
        ret = self.st_factor()
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret


if __name__ == '__main__':
    f = UpperShadowPct()
    f.result()
    f.save_result()
