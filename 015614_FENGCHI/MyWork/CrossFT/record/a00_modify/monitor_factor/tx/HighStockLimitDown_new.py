from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *

class HighStockLimitDown(crossFactor):
    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        stock_close = get_minute_1factor('close', start_datetime=self.cal_start,end_datetime=self.end, code_list=self.code_list)
        pre_close = get_daily_1factor('pre_close',self.cal_date_range,code_list=self.code_list)
        pre_close_min = pd.DataFrame(np.array(pre_close.loc[stock_close.index.get_level_values('date')]), index=stock_close.index,columns=stock_close.columns)
        stock_pct = stock_close/pre_close_min-1

        close = get_daily_1factor('close', self.cal_date_range, self.code_list)
        limit_max = get_daily_1factor('limit_max', self.cal_date_range, self.code_list)
        limit_min = get_daily_1factor('limit_min', self.cal_date_range, self.code_list)
        limit_min_min = pd.DataFrame(np.array(limit_min.loc[stock_close.index.get_level_values('date')]), index=stock_close.index,columns=stock_close.columns)

        stock_limit = (stock_close == limit_min_min)

        Limit_stock = (close == limit_max)
        stock_pool = clean_stock_list(no_ST=True, least_live_days=10, no_pause=True, least_recover_days=0).loc[self.start:self.end]

        HighStock = ((Limit_stock.rolling(3).sum() == 3) & (stock_pool == True)).shift(1).fillna(False)
        HighStock_min = pd.DataFrame(np.array(HighStock.loc[stock_close.index.get_level_values('date')]), index=stock_close.index,
                     columns=HighStock.columns)

        HighStockPct = (stock_limit & HighStock_min).sum(axis=1)
        HighStockPct = np.array(HighStockPct)[:, np.newaxis].repeat(len(self.code_list), axis=1)

        return HighStockPct

    def cal_groupst(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        self.factor =  self.st_factor()
        self.group = sameshape(self.factor, self.group_factor())

        #def cal_mean(x,axis):
        #    return np.nanmean(x,axis)

        self.func = self.group_func()
        res = st2groupst(self.factor, self.group, self.func)
        return arr_match_index(res,self.cal_date_range,self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.st_factor()

if __name__=='__main__':
    f = HighStockLimitDown(group='sw1', func='cross_mean',extend_days=5, author='tx', factor_name='HighStockLimitDown',
                        logic='连板高标日内跌停数量', freq='1min')
    f.save_result()

