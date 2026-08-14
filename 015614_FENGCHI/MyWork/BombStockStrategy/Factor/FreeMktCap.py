# coding: utf-8
# Author：fengchi863
# Date ：2021/9/10 13:35

'''
流通市值
'''

from BombStockStrategy.Factor.basic.crossFactor import crossFactor
from CrossFT.basic.crossUtils import *
from CrossFT.basic.operators import *
from BombStockStrategy.conf.path_conf import factor_path


class FreeMktCap(crossFactor):
    extend_days = 0
    author = 'fc'
    start = 20140701
    # start = 20210401
    end = 20210531
    logic = '流通市值'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': []}

    def st_factor(self):
        fmarketval = get_daily_1factor('fmarketval', date_list=self.cal_date_range, code_list=self.code_list)
        return fmarketval

    def cal_factor(self):
        fmarketval = self.st_factor() / 1e4
        ret = arr_match_index(fmarketval.values[:, None], self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.cal_factor()


if __name__ == '__main__':
    f = FreeMktCap()
    f.check_factor(f.result())
    f.save_result()
