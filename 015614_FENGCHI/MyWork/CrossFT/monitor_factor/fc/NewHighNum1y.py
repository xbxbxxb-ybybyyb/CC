# coding: utf-8
# Author：fengchi863
# Date ：2021/8/16 16:29

from basic.crossFactor import crossFactor
from basic.crossUtils import *


class NewHighNum1y(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 260
    author = 'fc'
    freq = 'daily'
    logic = '创新低的个股比例近一年'
    article = '市场监控结论'
    basic_datas = {'daily': ['close_badj']}

    def st_factor(self):
        close = self.database['daily']['close_badj']
        close = pd.DataFrame(close[:, 0, :], index=self.cal_date_range, columns=self.code_list)
        expanding_high = close.rolling(252).max()
        ret = close == expanding_high
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
    cal_factor()
    # val2 = cal_factor(numd={'daily': 10})
    # gap = abs(val1 - val2)
    # print(np.sum(np.where(np.isfinite(gap), gap, 0)))
