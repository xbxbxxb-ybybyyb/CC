# coding: utf-8
# Author：fengchi863
# Date ：2021/8/23 11:25

from basic.crossFactor import crossFactor
from basic.crossUtils import *


class UpDownAmtRatio26d(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=30
    author='fc'
    freq='daily'
    logic='前26日内上涨的成交量/下降的成交量'
    article='广发证券-20170330-多因子Alpha系列报告之三十'


    def st_factor(self):
        pctchg = get_daily_1factor('pct_chg', self.cal_date_range, self.code_list)
        vol = get_daily_1factor('volume', self.cal_date_range, self.code_list)
        pctchg = pctchg > 0
        pctchg[pctchg == 0] = -1
        pctchg[pctchg == 1] = 1
        ret = vol * pctchg
        ret2 = ret[ret > 0].fillna(0).rolling(26).sum() / ret[ret < 0].fillna(0).rolling(26).sum()
        ret2[ret2 == np.inf] = 0
        ret2[ret2 == -np.inf] = 0
        ret2 = df_match_index_col(ret2.applymap(abs), self.code_list, self.cal_date_range)
        return ret2

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    f = UpDownAmtRatio26d()
    f.save_result()