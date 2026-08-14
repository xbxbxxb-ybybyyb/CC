
from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


class xq_min_strong_ratio(crossFactor):
    cross_group='ones'
    cross_func='cross_mean'
    extend_days=0
    author='xq'
    logic='分钟全市场涨幅7%以上家数占比'
    article=None
    freq='1min'

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        close_min = get_minute_1factor('close', self.cal_date_range[0], self.cal_date_range[-1])
        pre_close = get_daily_1factor('pre_close', self.cal_date_range)
        close_min = df_match_index_col(close_min, self.code_list, self.cal_date_range, '1min')
        pre_close = df_match_index_col(pre_close, self.code_list, self.cal_date_range)  # np.array
        return close_min, pre_close

    def cal_groupst(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        close_min, pre_close = self.st_factor()
        pre_close = np.repeat(pre_close, 242, axis=1)
        pct_min = close_min / pre_close - 1
        self.group = sameshape(pct_min, self.group_factor())
        factor = st2groupst((pct_min>0.07), self.group, self.group_func())
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    val1 = cal_factor('data/user/016385/test/crossft/monitor_factor/xq', 'xq_min_strong_ratio.py', {'daily': 6}, notrun=False)
    val2 = cal_factor('data/user/016385/test/crossft/monitor_factor/xq', 'xq_min_strong_ratio.py',notrun=False)
    print(np.nansum(val1-val2))
    print(val1)