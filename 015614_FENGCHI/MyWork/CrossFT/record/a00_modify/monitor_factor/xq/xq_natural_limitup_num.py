
from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *



class xq_natural_limitup_num(crossFactor):
    cross_group='ones'
    cross_func='cross_sum'
    extend_days=40
    author='xq'
    logic='全市场非一字板涨停家数'
    article=None
    freq='daily'

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        limitup = get_daily_1factor('limit_up',self.cal_date_range)
        high = get_daily_1factor('high', self.date_range)
        low = get_daily_1factor('low', self.date_range)
        limit_max = get_daily_1factor('limit_max', self.date_range)
        yzb = (high == low) & (high == limit_max)
        natural_limitup = (limitup) & (~yzb)
        natural_limitup = df_match_index_col(natural_limitup, self.code_list, self.cal_date_range)# np.array
        return natural_limitup

    def cal_groupst(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        natural_limitup = self.st_factor()
        self.group = sameshape(natural_limitup, self.group_factor())
        factor = st2groupst(natural_limitup, self.group, self.group_func())
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    f = xq_natural_limitup_num()
    f.save_result()