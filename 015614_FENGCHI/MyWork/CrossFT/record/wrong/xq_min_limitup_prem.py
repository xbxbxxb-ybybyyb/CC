
from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *



class xq_min_limitup_prem(crossFactor):
    cross_group=None
    cross_func=None
    extend_days=40
    author='xq'
    logic='分钟涨停溢价'
    article=None
    freq='1min'

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        limitup = get_daily_1factor('limit_up',self.cal_date_range, self.code_list)
        close = get_daily_1factor('close', self.cal_date_range, self.code_list)
        high = get_daily_1factor('high', self.cal_date_range, self.code_list)
        low = get_daily_1factor('low', self.cal_date_range, self.code_list)
        ipo_date = get_daily_1factor('live_days', self.cal_date_range, self.code_list)
        ipo_one_board = ipo_date.copy()
        ipo_one_board[ipo_one_board == 1] = 0
        ipo_one_board.replace(0, np.nan, inplace=True)
        ipo_one_board[ipo_one_board>0] =1
        ipo_one_board = ((ipo_one_board*limitup).cumprod() == 1)& (high == low) | (ipo_date == 1)
        stk_pool = clean_stock_list(no_ST=True, least_live_days=1, no_pause=True, least_recover_days=0).loc[self.start:self.end]
        zt = ((ipo_one_board == 0) & limitup & stk_pool).astype(int).shift(1)
        zt = df_match_index_col(zt, self.code_list, self.cal_date_range)
        close_min = get_minute_1factor('close', self.cal_date_range[0], self.cal_date_range[-1])
        pre_close = get_daily_1factor('pre_close', self.cal_date_range)
        pre_close = pd.DataFrame(pre_close.loc[close_min.index.get_level_values('date')].values,
                                 index=close_min.index, columns=pre_close.columns)
        pct_min = close_min / pre_close - 1
        pct_min = df_match_index_col(pct_min, self.code_list, self.cal_date_range, '1min')
        return zt, pct_min

    def cal_groupst(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        zt, pct_min = self.st_factor()
        zt = np.repeat(zt, pct_min.shape[1], axis=1)
        zt_prem = np.nanmean(np.where(zt == 1, pct_min, np.nan), axis=2)
        factor = np.repeat(zt_prem, len(self.code_list), axis=1).reshape(zt_prem.shape[0], 242, len(self.code_list))
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
   val1 = cal_factor( )
