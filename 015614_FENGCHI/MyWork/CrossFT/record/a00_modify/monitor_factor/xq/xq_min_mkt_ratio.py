
from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


class xq_min_mkt_ratio(crossFactor):
    cross_group='ones'
    cross_func='cross_sum'
    author='xq'
    logic='全市场分钟涨跌比'
    article=None
    freq='1min'

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        close = get_minute_1factor('close_badj', self.cal_date_range[0], self.cal_date_range[-1])
        pct = close.pct_change(1)
        pct = df_match_index_col(pct, self.code_list, self.cal_date_range, '1min')# np.array
        return pct

    def cal_groupst(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        pct = self.st_factor()
        self.group = sameshape(pct, self.group_factor())
        up_num = st2groupst((pct > 0), self.group, self.group_func())
        down_num = st2groupst((pct < 0), self.group, self.group_func())
        factor = up_num/down_num
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    f = xq_min_mkt_ratio()
    f.save_result()