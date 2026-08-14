
from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


class xq_mkt_amt(crossFactor):
    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        amt = get_daily_1factor('amt',self.cal_date_range).rolling(5, min_periods=1).apply(np.nanmean)
        amt = df_match_index_col(amt, self.code_list, self.cal_date_range)# np.array
        return amt

    def cal_groupst(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        amt = self.st_factor()
        self.group = sameshape(amt, self.group_factor())
        factor = st2groupst(amt, self.group, self.group_func())
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()

if __name__=='__main__':
    group , func = 'ones', 'cross_sum'
    print('-------------{}-----------{}-------------'.format(group,func))
    f = xq_mkt_amt(group, func, 40, 20170101, 20210531, 'xq', 'xq_mkt_amt', '全市场5日平均成交额',
                   article=None,freq='daily')
    f.save_result()