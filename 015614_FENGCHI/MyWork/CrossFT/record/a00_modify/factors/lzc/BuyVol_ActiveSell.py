# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : BuyVol_ActiveSell.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


class BuyVol_ActiveSell(crossFactor):
    cross_group='sw1'
    cross_func='cross_sum'
    extend_days=0
    author='lzc'
    logic='T日买入成交量和主动卖出成交量;两者绝对值差值代表了知情交易者概率;组内取ZSCORE*因子值'
    article=''
    freq='daily'

    window = 15

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        buyorderamt = get_minute_pickle('buyorderamt', date_list=self.cal_date_range, code_list=self.code_list)
        activesellorderamt = get_minute_pickle('activesellorderamt', date_list=self.cal_date_range, code_list=self.code_list)
        buyorderamt = buyorderamt.groupby(level=0).sum()
        activesellorderamt = activesellorderamt.groupby(level=0).sum()
        return df_match_index_col(buyorderamt, self.code_list, self.cal_date_range), \
               df_match_index_col(activesellorderamt, self.code_list, self.cal_date_range)

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        buyorderamt, activesellorderamt = self.st_factor()
        self.group = sameshape(buyorderamt, self.group_factor())
        group_buyorderamt = st2groupst(buyorderamt, self.group, cross_sum)
        group_activesellorderamt = st2groupst(activesellorderamt, self.group, cross_sum)

        stk_diff = buyorderamt - activesellorderamt
        group_diff = group_buyorderamt - group_activesellorderamt

        stk_zscore = (stk_diff - st2groupst(stk_diff, self.group, cross_mean)) / st2groupst(stk_diff, self.group, cross_std)

        return arr_match_index(stk_zscore * group_diff, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    f = BuyVol_ActiveSell()
    f.save_result()