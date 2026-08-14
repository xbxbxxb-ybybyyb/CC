# coding: utf-8
# Author：fengchi863
# Date ：2021/8/24 13:39

import talib

from basic.crossFactor import crossFactor
from basic.crossUtils import *


class RSI12d(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=30
    author='fc'
    freq='daily'
    logic='个股12天相对强弱系数行业内求均值'
    article='渤海证券20180710–行业轮动专题一'


    def st_factor(self):
        close = get_daily_1factor('close_badj', self.cal_date_range, self.code_list)
        rsi = {}
        for stk in close.columns:
            try:
                rsi[stk] = talib.RSI(close[stk].values, timeperiod=12)
            except:
                rsi[stk] = np.array([np.nan] * len(close.index))
        ret = pd.DataFrame(rsi)
        ret.index = close.index
        return ret

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    f = RSI12d()
    f.save_result()