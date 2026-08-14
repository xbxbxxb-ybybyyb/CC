
from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


class xq_min_limitup_num(crossFactor):
    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        limit_max = get_daily_1factor('limit_max',self.cal_date_range)
        limit_max = df_match_index_col(limit_max, self.code_list, self.cal_date_range)
        close = get_minute_1factor('close', self.cal_date_range[0], self.cal_date_range[-1])
        close = df_match_index_col(close, self.code_list, self.cal_date_range, '1min')
        return limit_max, close

    def cal_groupst(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        limit_max, close = self.st_factor()
        print('基础因子加载完毕')
        limit_max = np.repeat(limit_max, 242, axis=1)
        self.group = sameshape(limit_max, self.group_factor())
        zt = (limit_max == close)
        group_zt = st2groupst(zt, self.group, cross_sum)
        print('因子计算完毕')
        return arr_match_index(group_zt, self.cal_date_range, self.date_range)

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
    f = xq_min_limitup_num(group, func, 40, 20170101, 20210531, 'xq', 'xq_min_limitup_num', '分钟全市场涨停家数',
                       article=None, freq='1min')
    f.save_result()
