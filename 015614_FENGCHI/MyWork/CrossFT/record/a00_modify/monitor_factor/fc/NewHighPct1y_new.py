# coding: utf-8
# Author：fengchi863
# Date ：2021/8/17 13:20

from basic.crossFactor import crossFactor
from basic.crossUtils import *


class NewHighPct1y(crossFactor):
    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        close = get_daily_1factor('close_badj', self.cal_date_range)
        expanding_high = close.expanding(250).max()
        high_num = close == expanding_high
        total = (~pd.isna(close)).sum(axis=1)
        ret = high_num.sum(axis=1) / total
        a = pd.DataFrame(np.repeat([ret.values], len(self.code_list), axis=0).T, index=self.cal_date_range, columns=self.code_list)
        factor = df_match_index_col(a, self.code_list, self.date_range)
        return factor

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.st_factor()


if __name__ == '__main__':
    f = NewHighPct1y(group=None,
                     func=None,
                     extend_days=260,
                     start=20170101,
                     end=20210531,
                     author='fc',
                     factor_name='NewHighPct1y',
                     freq='daily',
                     logic='创新低的个股比例(近一年)',
                     article='市场监控结论')
    f.save_result()