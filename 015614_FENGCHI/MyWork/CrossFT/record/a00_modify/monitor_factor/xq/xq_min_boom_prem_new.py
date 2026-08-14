
from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *



class xq_min_boom_prem(crossFactor):
    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        limit_max = get_daily_1factor('limit_max',self.cal_date_range)
        close = get_daily_1factor('close', self.cal_date_range)
        high = get_daily_1factor('high', self.cal_date_range)
        boom = ((high == limit_max) & (close < limit_max)).shift(1)
        boom = df_match_index_col(boom, self.code_list, self.cal_date_range)
        close_min = get_minute_1factor('close', self.cal_date_range[0], self.cal_date_range[-1])
        pre_close = get_daily_1factor('pre_close', self.cal_date_range)
        pre_close = pd.DataFrame(pre_close.loc[close_min.index.get_level_values('date')].values,
                                 index=close_min.index, columns=pre_close.columns)
        pct_min = close_min / pre_close - 1
        pct_min = df_match_index_col(pct_min, self.code_list, self.cal_date_range, '1min')
        return boom, pct_min

    def cal_groupst(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        boom, pct_min = self.st_factor()
        boom = np.repeat(boom, pct_min.shape[1], axis=1)
        boom_prem = np.where(boom == 1, pct_min, np.nan)
        self.group = sameshape(boom, self.group_factor())
        factor = st2groupst(boom_prem, self.group, self.group_func())
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
    f = xq_min_boom_prem(group, func, 40, 20170101, 20210531, 'xq', 'xq_min_boom_prem', '分钟炸板股溢价率',
                         article=None, freq='1min')
    f.save_result()
