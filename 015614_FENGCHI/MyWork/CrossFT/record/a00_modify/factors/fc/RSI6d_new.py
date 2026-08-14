# coding: utf-8
# Author：fengchi863
# Date ：2021/8/24 11:00

from basic.crossFactor import crossFactor
from basic.crossUtils import *
import talib


class RSI6d(crossFactor):

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
    group, func = 'sw1', 'cross_mean'
    print('-------------{}-----------{}-------------'.format(group, func))
    f = RSI6d(group=group,
              func=func,
              extend_days=30,
              start=20170101,
              end=20210531,
              author='fc',
              factor_name='RSI6d',
              freq='daily',
              logic='个股6天相对强弱系数行业内求均值',
              article='渤海证券 20180710 – 行业轮动专题一')
    f.save_result()
