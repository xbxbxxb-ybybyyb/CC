# coding: utf-8
# Author：fengchi863
# Date ：2021/8/17 14:20

from basic.crossFactor import crossFactor
from basic.crossUtils import *


class NewHighDivLow1y(crossFactor):
    cross_group=None
    cross_func=None
    extend_days=260
    author='fc'
    freq='daily'
    logic='创新低的个股比'
    basic_datas = {'daily': ['close_badj']}

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        epsilon = 1e-1
        close = self.database['daily']['close_badj']
        close = pd.DataFrame(close[:, 0, :], index=self.cal_date_range, columns=self.code_list)
        expanding_high = close.rolling(252).max()
        expanding_low = close.rolling(252).min()
        ret1 = close == expanding_high
        ret2 = close == expanding_low
        pct_factor = ret1.sum(axis=1) / (ret2.sum(axis=1) + epsilon)
        a = pd.DataFrame(np.repeat([pct_factor.values], len(self.code_list), axis=0).T, index=self.cal_date_range,
                         columns=self.code_list)
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
    # f = NewHighDivLow1y()
    # f.save_result()

    val = cal_factor('/data/user/015614/MyWork/CrossFT/monitor_factor/fc', 'NewHighDivLow1y.py', {'daily': 6}, notrun=False)