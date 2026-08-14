# coding: utf-8
# Author：fengchi863
# Date ：2021/8/17 14:18

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *


class NewLowPct1y_5m(crossFactor):
    cross_group = None
    cross_func = None
    extend_days = 260
    author = 'fc'
    freq = '5mins'
    logic = '创新低的个股比例近一年'
    basic_datas = {'daily': ['close_badj'], '30mins': [], '5mins': ['close_badj'], '1min': []}

    def st_factor(self):
        daily_close = self.database['daily']['close_badj']
        min_close = self.database['5mins']['close_badj']
        expanding_low = dt_min(daily_close, 252)
        min_close_min = dt_min(min_close, 48)

        ret = (min_close < expanding_low) & (min_close == min_close_min)
        pct_factor = np.nansum(ret, axis=2) / np.nansum(np.isfinite(ret), axis=2)
        return arr_match_index(np.repeat(pct_factor[:, :, None], len(self.code_list), axis=2),
                               self.cal_date_range, self.date_range)

    def result(self):
        return self.st_factor()


if __name__ == '__main__':
    cal_factor()
