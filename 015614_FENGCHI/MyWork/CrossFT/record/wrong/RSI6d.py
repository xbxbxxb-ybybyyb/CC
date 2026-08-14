# coding: utf-8
# Author：fengchi863
# Date ：2021/8/24 11:00

from basic.crossFactor import crossFactor
from basic.crossUtils import *
import talib

'''
因为调用外部函数RSI，暂时没找到错误原因
'''

class RSI6d(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=250
    author='fc'
    freq='daily'
    logic='个股6天相对强弱系数行业内求均值'
    article='渤海证券20180710–行业轮动专题一'


    def st_factor(self):
        close = get_daily_1factor('close_badj', self.cal_date_range, self.code_list)
        rsi = {}
        for stk in close.columns:
            try:
                rsi[stk] = talib.RSI(close[stk].values, timeperiod=6)
            except:
                rsi[stk] = np.array([np.nan] * len(close.index))
        ret = pd.DataFrame(rsi)
        ret.index = close.index
        return ret

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    # f = RSI6d()
    # print(f.result())

    val = cal_factor('/data/user/015614/MyWork/CrossFT/factors/fc', 'RSI6d.py', {'daily': 6}, notrun=False)
