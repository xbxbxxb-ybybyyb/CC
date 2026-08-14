from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *

class ConceptBenchStockPctInday(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    author = 'tx'
    extend_days = 240
    logic = '板块标杆股日内涨跌幅'
    freq = '1min'

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        stock_close = get_minute_1factor('close', start_datetime=self.cal_start,end_datetime=self.end, code_list=self.code_list)
        pre_close = get_daily_1factor('pre_close',self.cal_date_range,code_list=self.code_list)
        pre_close_min = pd.DataFrame(np.array(pre_close.loc[stock_close.index.get_level_values('date')]), index=stock_close.index,columns=stock_close.columns)
        stock_pct = stock_close/pre_close_min-1
        # 输出市场标杆股
        # 1、均线排列纯多头
        close_badj = get_daily_1factor('close_badj', code_list=self.code_list)
        line5 = close_badj.rolling(5).mean()
        line10 = close_badj.rolling(10).mean()
        line20 = close_badj.rolling(20).mean()
        line30 = close_badj.rolling(30).mean()
        line60 = close_badj.rolling(60).mean()
        line240 = close_badj.rolling(240).mean()
        BenchMarkStock = ((close_badj > line10) & (line5 > line10) & (line10 > line20) & (line20 > line30) & (
                    line30 > line60) & (line60 > line240))
        # 2、涨跌幅
        Max_Pct = close_badj.pct_change(20).rank(pct=True, axis=1)
        PctStock = ((Max_Pct > 0.95) & (Max_Pct > 0.4))
        # 3、涨停数量
        limit_max = get_daily_1factor('limit_max', date_list=self.cal_date_range,code_list=self.code_list)
        close = get_daily_1factor('close', date_list=self.cal_date_range,code_list=self.code_list)
        Limit_Time = ((limit_max == close).rolling(40).sum() >= 3)
        # 4、市场股票池
        code_list = clean_stock_list(no_ST=True, least_live_days=10, least_recover_days=2)
        # 5、位于最近新高附近
        high_position = (1 - close_badj / close_badj.rolling(120).max() < 0.2)
        TodayBest = (BenchMarkStock.rolling(5).sum() == 5) & Limit_Time & PctStock & code_list
        # 最终结果
        StockChoice = ((TodayBest.rolling(10).max() == True) & high_position).loc[self.cal_date_range, self.code_list]
        StockChoice_min = pd.DataFrame(np.array(StockChoice.loc[stock_close.index.get_level_values('date')]),
                                     index=stock_close.index,columns=StockChoice.columns)

        NewStockPct = stock_pct[StockChoice_min]
        result = df_match_index_col(NewStockPct, self.code_list, self.cal_date_range, '1min')  # np.array

        return result

    def cal_groupst(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        self.factor = self.st_factor()
        self.group = sameshape(self.factor, self.group_factor())

        # def cal_mean(x,axis):
        #    return np.nansum(x,axis)

        self.func = self.group_func()
        res = st2groupst(self.factor, self.group, self.func)
        return arr_match_index(res, self.cal_date_range, self.date_range)


    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return arr_match_index(self.st_factor(), self.cal_date_range, self.date_range)

if __name__ == '__main__':
    f = ConceptBenchStockPctInday()
    f.save_result()

