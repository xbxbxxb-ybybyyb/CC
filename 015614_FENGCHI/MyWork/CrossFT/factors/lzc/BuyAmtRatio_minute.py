# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : BuyAmtRatio_minute.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


class BuyAmtRatio_minute(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 0
    author = 'lzc'
    logic = '个股买入成交占比组内ZSCORE*分组买入成交占比'
    article = ''
    freq = '5mins'

    window = 15
    basic_datas = {'daily': [], '30mins': [], '5mins': ['amt', 'buyorderamt'], '1min': []}

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return [self.database['5mins'][x] for x in ['amt', 'buyorderamt']]

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        amt, buyorderamt = self.st_factor()
        self.group = sameshape(amt, self.group_factor())
        group_amt = st2groupst(amt, self.group, cross_sum)
        group_buyorderamt = st2groupst(buyorderamt, self.group, cross_sum)

        stk_ratio = buyorderamt / amt
        group_ratio = group_buyorderamt / group_amt

        stk_zscore = (stk_ratio - st2groupst(stk_ratio, self.group, cross_mean)) / st2groupst(stk_ratio, self.group, cross_std)

        return arr_match_index(stk_zscore * group_ratio, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    cal_factor()

    # val1 = cal_factor(numd={})
    # val2 = cal_factor(numd={'5mins': 10})
    # gap = abs(val1 - val2)
    # print('mae:', np.sum(np.where(np.isfinite(gap), gap, 0)))
