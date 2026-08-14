# coding: utf-8
# Author：fengchi863
# Date ：2021/8/17 11:19

from basic.crossFactor import crossFactor
from basic.crossUtils import *


class NewLowNum1y(crossFactor):
    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        close = get_daily_1factor('close_badj', self.cal_date_range)
        expanding_low = close.expanding(250).min()
        ret = close == expanding_low
        ret = ret.applymap(int)
        ret = ret.sum(axis=1)
        ret = index2st(ret.values.reshape(-1, 1), len(self.code_list))
        return arr_match_index(ret, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.st_factor()


if __name__ == '__main__':
    f = NewLowNum1y(group=None,
                    func=None,
                    extend_days=260,
                    start=20170101,
                    end=20210531,
                    author='fc',
                    factor_name='NewLowNum1y',
                    freq='daily',
                    logic='创新低的个股比例(近一年)',
                    article='市场监控结论')
    f.save_result()
