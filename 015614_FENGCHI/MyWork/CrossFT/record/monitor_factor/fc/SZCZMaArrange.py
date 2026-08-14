# coding: utf-8
# Author：fengchi863
# Date ：2021/8/18 14:20

from basic.crossFactor import crossFactor
from basic.crossUtils import *


class SZCZMaArrange(crossFactor):
    def st_factor(self):
        close = get_daily_1factor('close', code_list=['SZCZ'], date_list=self.cal_date_range, type='bench')
        ma5 = close.rolling(5).mean()
        ma10 = close.rolling(10).mean()
        ma20 = close.rolling(20).mean()
        ma60 = close.rolling(60).mean()
        add1 = (ma5 > ma10).applymap(int)
        add2 = (ma10 > ma20).applymap(int)
        add3 = (ma20 > ma60).applymap(int)
        factor = add1 + add2 + add3
        factor = index2st(factor.values.reshape(-1, 1), len(self.code_list))
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        return self.st_factor()


if __name__ == '__main__':
    f = SZCZMaArrange(group=None,
                      func=None,
                      extend_days=60,
                      start=20170101,
                      end=20210531,
                      author='fc',
                      factor_name='SZCZMaArrange',
                      freq='daily',
                      logic='深证成指均线排列情况',
                      article='市场监控结论')
    f.save_result()
