# coding: utf-8
# Author：fengchi863
# Date ：2021/8/30 10:15

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import ts_cumcorr2
from basic.crossOperators import *

'''
日内量价相关性
4090秒计算完成
'''


class GroupSzzzStkCorr(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 5
    author = 'fc'
    freq = '1min'
    logic = '板块内涨跌幅加权平均与上证指数的相关性'
    article = ''
    basic_datas = {'daily': ['pre_close', 'close_SZZZ'], '30mins': [], '5mins': [], '1min': ['close', 'close_SZZZ']}

    def st_factor(self):
        close = self.database['1min']['close']
        szzz_close = self.database['1min']['close_SZZZ']
        pre_close = self.database['daily']['pre_close']
        szzz_daily_close = self.database['daily']['close_SZZZ']
        stk_pct = close / pre_close - 1
        szzz_pct = szzz_close / dt_delay(szzz_daily_close, 1)
        return stk_pct, szzz_pct

    def calc_factor(self):
        stk_pct, szzz_pct = self.st_factor()
        szzz_pct = np.repeat(szzz_pct, len(self.code_list), axis=2)
        ret = ts_cumcorr2(stk_pct, szzz_pct)
        self.group = sameshape(ret, self.group_factor())
        ret = st2groupst(ret, self.group,  self.group_func())
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.calc_factor()


if __name__ == '__main__':
    # f = GroupSzzzStkCorr()
    # print(f.result())
    # f.save_result()

    cal_factor()
