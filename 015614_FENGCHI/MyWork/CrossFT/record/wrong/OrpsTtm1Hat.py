# coding: utf-8
# Author：fengchi863
# Date ：2021/9/8 16:37

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class OrpsTtm1Hat(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 250
    author = 'fc'
    start = 20140701
    # start = 20210401
    end = 20210531
    freq = 'daily'
    logic = '每股营业收入增长率-组内每股营业收入均值增长率'
    article = ''
    basic_datas = {'daily': ['orps_ttm'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        orps_ttm = self.database['daily']['orps_ttm']
        return orps_ttm

    def calc_groupst(self):
        orps_ttm = self.st_factor()
        self.group = sameshape(orps_ttm, self.group_factor())
        group_orps_ttm = st2groupst(orps_ttm, self.group,  self.group_func())
        d_orps_ttm = dt_delta(orps_ttm, 250)
        d_group_orps_ttm = dt_delta(group_orps_ttm, 250)
        ret = d_orps_ttm - d_group_orps_ttm
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_groupst()


if __name__ == '__main__':
    f = OrpsTtm1Hat()
    f.save_result()
