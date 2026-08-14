
from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *



class xq_continuous_limitup_ratio(crossFactor):
    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        limitup = get_daily_1factor('limit_up',self.cal_date_range)
        close = get_daily_1factor('close', self.cal_date_range)
        high = get_daily_1factor('high', self.cal_date_range)
        low = get_daily_1factor('low', self.cal_date_range)
        ipo_date = get_daily_1factor('live_days', self.cal_date_range)
        ipo_one_board = ipo_date.copy()
        ipo_one_board[ipo_one_board == 1] = 0
        ipo_one_board.replace(0, np.nan, inplace=True)
        ipo_one_board[ipo_one_board>0] =1
        ipo_one_board = ((ipo_one_board*limitup).cumprod() == 1) & (high == low) | (ipo_date == 1)
        stk_pool = clean_stock_list(no_ST=True, least_live_days=1, no_pause=True, least_recover_days=0).loc[self.start:self.end]
        zt = ((ipo_one_board == 0) & limitup & stk_pool)
        lb = (zt.rolling(2).sum() == 2)
        zt_yes = zt.shift(1)
        lb = df_match_index_col(lb, self.code_list, self.cal_date_range)
        zt_yes = df_match_index_col(zt_yes, self.code_list, self.cal_date_range)
        return lb, zt_yes

    def cal_groupst(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        lb, zt_yes = self.st_factor()
        self.group = sameshape(lb, self.group_factor())
        lb_num = st2groupst(lb, self.group, self.group_func())
        zt_num = st2groupst(zt_yes, self.group, self.group_func())
        zt_num = np.where(zt_num == 0, 1, zt_num)
        factor = lb_num/zt_num
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
    f = xq_continuous_limitup_ratio(group, func, 60, 20170101, 20210531, 'xq', 'xq_continuous_limitup_ratio', '连板率',
                                  article=None, freq='daily')
    f.save_result()
