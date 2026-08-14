# coding: utf-8
# Author：fengchi863
# Date ：2021/8/18 14:20

from basic.crossFactor import crossFactor
from basic.crossUtils import *


class MaArrange(crossFactor):
    cross_group=None
    cross_func=None
    extend_days=60
    author='fc'
    freq='daily'
    logic='均线排列情况'
    article='市场监控结论'

    def st_factor(self):
        close = get_daily_1factor('close', date_list=self.cal_date_range)
        ma5 = close.rolling(5).mean()
        ma10 = close.rolling(10).mean()
        ma20 = close.rolling(20).mean()
        ma60 = close.rolling(60).mean()
        add1 = (ma5 > ma10).applymap(int)
        add2 = (ma10 > ma20).applymap(int)
        add3 = (ma20 > ma60).applymap(int)
        factor = add1 + add2 + add3
        factor = df_match_index_col(factor, self.code_list, self.date_range)
        return factor

    def result(self):
        return self.st_factor()


if __name__ == '__main__':
    f = MaArrange()
    f.save_result()