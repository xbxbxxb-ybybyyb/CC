# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : BuyAmtRatio.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


class BuyAmtRatio(crossFactor):
    window = 15

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        amt = get_minute_pickle('amt', date_list=self.cal_date_range, code_list=self.code_list)
        buyorderamt = get_minute_pickle('buyorderamt', date_list=self.cal_date_range, code_list=self.code_list)
        amt = amt.groupby(level=0).sum()
        buyorderamt = buyorderamt.groupby(level=0).sum()
        return df_match_index_col(amt, self.code_list, self.cal_date_range), \
               df_match_index_col(buyorderamt, self.code_list, self.cal_date_range)

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
    # for group in groups:
    #     for func in funcs:
    #         print('-------------{}-----------{}-------------'.format(group,func))
    f = BuyAmtRatio('sw1', 'cross_sum', 0, 20170101, 20210531, author='lzc', factor_name='BuyAmtRatio',
                    logic='个股买入成交占比组内ZSCORE*分组买入成交占比', \
                    article='', freq='daily')
    e = time.time()
    # f.result()
    f.save_result()
    print(f'total calc time {time.time() - e}')
    # send_message(['015664'],f'total calc time {time.time()-e}')
