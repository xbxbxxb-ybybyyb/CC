
from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


class xq_min_amt_5e_pct(crossFactor):
    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        amt = get_daily_1factor('amt', self.cal_date_range).shift(1)/(10**5)
        close_min = get_minute_1factor('close', self.cal_date_range[0], self.cal_date_range[-1])
        pre_close = get_daily_1factor('pre_close', self.cal_date_range)
        pre_close = pd.DataFrame(pre_close.loc[close_min.index.get_level_values('date')].values,
                                 index=close_min.index, columns=pre_close.columns)
        pct_min = close_min/pre_close-1
        pct_min = df_match_index_col(pct_min, self.code_list, self.cal_date_range, '1min')
        amt = df_match_index_col(amt, self.code_list, self.cal_date_range)
        return amt, pct_min

    def cal_groupst(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        amt, pct_min = self.st_factor()
        self.group = sameshape(pct_min, self.group_factor())
        active_stk_pct = np.where(np.repeat(amt, 242, axis=1) > 5, pct_min, np.nan)
        factor = st2groupst(active_stk_pct, self.group, self.group_func())
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    group, func = 'ones', 'cross_mean'
    print('-------------{}-----------{}-------------'.format(group, func))
    f = xq_min_amt_5e_pct(group=group, func=func, author='xq', factor_name='xq_min_amt_5e_pct',logic='成交额5亿以上股票平均涨幅', article=None, freq='1min')
    f.save_result()