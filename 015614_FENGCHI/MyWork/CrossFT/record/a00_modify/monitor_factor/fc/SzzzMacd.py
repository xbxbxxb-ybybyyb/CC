# coding: utf-8
# Author：fengchi863
# Date ：2021/8/17 14:48

import talib

from basic.crossFactor import crossFactor
from basic.crossUtils import *


class SzzzMacd(crossFactor):
    cross_group=None
    cross_func=None
    extend_days=260
    author='fc'
    freq='daily'
    logic='上证综指MACD'
    article='市场监控结论'

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        close = get_daily_1factor('close', code_list=['SZZZ'], date_list=self.cal_date_range, type='bench')
        _, _, a3 = talib.MACD(close['SZZZ'].values, fastperiod=12,
                              slowperiod=26, signalperiod=9)
        a = index2st(a3.reshape(-1, 1), len(self.code_list))
        # a = pd.DataFrame(np.repeat([a3], len(self.code_list), axis=0).T, index=self.cal_date_range,
        #                  columns=self.code_list)
        # factor = df_match_index_col(a, self.code_list, self.cal_date_range)
        return arr_match_index(a, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.st_factor()


if __name__ == '__main__':
    f = SzzzMacd()
    f.save_result()