
from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


class xq_limitdown_num(crossFactor):
    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        limitdown = get_daily_1factor('limit_down',self.cal_date_range)
        limitdown = df_match_index_col(limitdown, self.code_list, self.cal_date_range)# np.array
        return limitdown

    def cal_groupst(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        limitdown = self.st_factor()
        self.group = sameshape(limitdown, self.group_factor())
        factor = st2groupst(limitdown, self.group, self.group_func())
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    group, func = 'ones', 'cross_sum'
    print('-------------{}-----------{}-------------'.format(group, func))
    f = xq_limitdown_num(group, func, 40, 20170101, 20210531, 'xq', 'xq_limitdown_num', '全市场跌停家数',
                         article=None, freq='daily')
    f.save_result()
