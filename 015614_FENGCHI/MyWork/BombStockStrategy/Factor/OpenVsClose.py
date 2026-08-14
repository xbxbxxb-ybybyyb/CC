# coding: utf-8
# Author：fengchi863
# Date ：2021/11/5 14:34

from BombStockStrategy.Factor.basic.crossFactor import crossFactor
from CrossFT.basic.crossUtils import *
from CrossFT.basic.operators import *
from BombStockStrategy.conf.path_conf import factor_path


class OpenVsClose(crossFactor):
    extend_days = 10
    author = 'fc'
    logic = '开盘价与收盘价的比较'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['open_badj', 'close_badj']}

    def st_factor(self):
        close_badj = self.database['daily']['close_badj']
        open_badj = self.database['daily']['open_badj']
        ret = (open_badj < close_badj).astype(int)
        return ret

    def result(self):
        ret = self.st_factor()
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret


if __name__ == '__main__':
    f = OpenVsClose()
    f.check_factor(f.result())
    f.save_result()
