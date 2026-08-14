from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *

class NewStockDailyUpNumWeight(crossFactor):
    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        # 输出次新股
        close = get_daily_1factor('close', self.cal_date_range, self.code_list)
        high = get_daily_1factor('high', self.cal_date_range, self.code_list)
        low = get_daily_1factor('low', self.cal_date_range, self.code_list)

        limit_max = get_daily_1factor('limit_max', self.cal_date_range, self.code_list)
        Limit_stock = (close == limit_max)

        ipo_date = get_daily_1factor('live_days', date_list=self.cal_date_range)
        ipo_one_board =ipo_date.copy()
        ipo_one_board[ipo_one_board == 1] = 0
        ipo_one_board.replace(0, np.nan, inplace=True)  # 把未上市之前的日期都变为0
        ipo_one_board[ipo_one_board > 0] = 1  # 上市之后的时间都标记为1
        ipo_one_board = (((ipo_one_board * Limit_stock).cumprod() == 1) & (high == low)) | (ipo_date == 1)
        stock_pool = clean_stock_list(no_ST=True, least_live_days=1, no_pause=True, least_recover_days=0).loc[self.start:self.end]
        stock_pool = (ipo_one_board == 0) & stock_pool

        stock_pool1 = clean_stock_list(no_ST=True, least_live_days=200, no_pause=True, least_recover_days=0).loc[self.start:self.end]

        NewStock = ((stock_pool==True) & (stock_pool1==False))

        stock_pct = get_daily_1factor('pct_chg', self.cal_date_range, self.code_list)

        NewStockPct = (stock_pct[NewStock]>0).sum(axis=1)/NewStock.sum(axis=1)

        NewStockPct = np.array(NewStockPct)[:, np.newaxis].repeat(len(self.code_list), axis=1)

        return NewStockPct

    def cal_groupst(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        self.factor =  self.st_factor()
        self.group = sameshape(self.factor, self.group_factor())

        def cal_mean(x,axis):
            return np.nansum(x,axis)

        self.func = cal_mean
        res = st2groupst(self.factor, self.group, self.func)


        return arr_match_index(res,self.cal_date_range,self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return arr_match_index(self.st_factor(), self.cal_date_range, self.date_range)

if __name__=='__main__':
    f = NewStockDailyUpNumWeight(group='sw1', func=None,author='tx',extend_days=10,
                              factor_name='NewStockDailyUpNumWeight',logic='次新股上涨数量',freq='daily')
    f.save_result()





