
from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *



class xq_boom_ratio(crossFactor):
    cross_group='ones'
    cross_func='cross_sum'
    extend_days=60
    author='xq'
    logic='炸板率'
    article=None
    freq='daily'

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        limitup = get_daily_1factor('limit_up',self.cal_date_range, self.code_list)
        close = get_daily_1factor('close', self.cal_date_range, self.code_list)
        high = get_daily_1factor('high', self.cal_date_range, self.code_list)
        low = get_daily_1factor('low', self.cal_date_range, self.code_list)
        limit_max = get_daily_1factor('limit_max', self.cal_date_range, self.code_list)
        ipo_date = get_daily_1factor('live_days', self.cal_date_range, self.code_list)
        ipo_one_board = ipo_date.copy()
        ipo_one_board[ipo_one_board == 1] = 0
        ipo_one_board.replace(0, np.nan, inplace=True)
        ipo_one_board[ipo_one_board>0] =1
        ipo_one_board = ((ipo_one_board*limitup).cumprod() == 1) & (high == low) | (ipo_date == 1)
        stk_pool = clean_stock_list(no_ST=True, least_live_days=1, no_pause=True, least_recover_days=0).loc[self.cal_start:self.end]
        zt = ((ipo_one_board == 0) & limitup & stk_pool)
        boom = (limit_max == high) & (close < limit_max) & stk_pool & (ipo_one_board == 0)
        boom = df_match_index_col(boom, self.code_list, self.cal_date_range)
        zt = df_match_index_col(zt, self.code_list, self.cal_date_range)
        return zt, boom

    def cal_groupst(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        zt, boom = self.st_factor()
        self.group = sameshape(zt, self.group_factor())
        zt_num = st2groupst(zt, self.group, self.group_func())
        boom_num = st2groupst(boom, self.group, self.group_func())
        factor = boom_num/(zt_num + boom_num)
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    f = xq_boom_ratio()
    f.save_result()