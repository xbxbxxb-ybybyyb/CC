# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : ActiveBuySellPressureStd.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


class ActiveBuySellPressureStd(crossFactor):
    cross_group='sw1'
    cross_func='cross_sum'
    extend_days=0
    author='lzc'
    logic='个股日内主动买入卖出成交额之比的波动率组内Zscore*分组比的波动率'
    article=''
    freq='daily'

    window = 15

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        activebuyorderamt = get_minute_pickle('activebuyorderamt', date_list=self.cal_date_range, code_list=self.code_list)
        activesellorderamt = get_minute_pickle('activesellorderamt', date_list=self.cal_date_range, code_list=self.code_list)

        return df_match_index_col(activebuyorderamt, self.code_list, self.cal_date_range, freq='1min'), \
               df_match_index_col(activesellorderamt, self.code_list, self.cal_date_range, freq='1min')

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        activebuyorderamt, activesellorderamt = self.st_factor()
        group_1min = sameshape(activebuyorderamt, self.group_factor())

        group_activebuy = st2groupst(activebuyorderamt, group_1min, cross_sum)
        group_activesell = st2groupst(activebuyorderamt, group_1min, cross_sum)

        stk_inter_ratio = activebuyorderamt / activesellorderamt
        group_inter_ratio = group_activebuy / group_activesell

        stk_std = np.nanstd(stk_inter_ratio, axis=1)
        group_std = np.nanstd(group_inter_ratio, axis=1)

        group_day = sameshape(stk_std, self.group_factor())
        stk_zscore = (stk_std - st2groupst(stk_std, group_day, cross_mean)) / st2groupst(stk_std, group_day, cross_std)

        return arr_match_index(stk_zscore * group_std, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    f = ActiveBuySellPressureStd()
    f.save_result()