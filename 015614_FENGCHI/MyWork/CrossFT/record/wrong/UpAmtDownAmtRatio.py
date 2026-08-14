# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : UpAmtDownAmtRatio.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class UpAmtDownAmtRatio(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 15
    author = 'lzc'
    logic = '上行成交额与下行成交额之比*分组的该因子'
    article = '招商证券	20200618	琢璞系列报告017'
    freq = 'daily'
    basic_datas = {'daily': [], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        amt = get_minute_1factor('amt')
        close_badj = get_minute_1factor('close_badj').shift(1)

        return df_match_index_col(close_badj, self.code_list, self.cal_date_range, freq='1min'), \
               df_match_index_col(amt, self.code_list, self.cal_date_range, freq='1min')
    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        close_badj, amt = self.st_factor()
        min_group = sameshape(close_badj, self.group_factor())
        ret = close_badj / delay(close_badj) - 1
        up_amt = np.where(ret > 0, amt, 0)
        down_amt = np.where(ret < 0, amt, 0)
        stk_upamt_daily = np.nansum(up_amt, axis=1)  # /np.nansum(down_amt,axis=1)
        stk_downamt_daily = np.nansum(down_amt, axis=1)

        stk_ratio = stk_upamt_daily / stk_downamt_daily

        daily_group = sameshape(stk_ratio, self.group_factor())

        group_ratio = st2groupst(stk_upamt_daily, daily_group, cross_sum) / st2groupst(stk_downamt_daily, daily_group, cross_sum)

        stk_zscore = (stk_ratio - st2groupst(stk_ratio, daily_group, cross_mean)) / st2groupst(stk_ratio, daily_group, cross_std)

        return arr_match_index(stk_zscore * group_ratio, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':

    val2 = cal_factor(numd={'daily': 15})


