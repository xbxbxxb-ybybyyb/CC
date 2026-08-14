from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *

class BenchMarkStockPct5day(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    author='tx'
    extend_days = 280
    logic='市场标杆股5日涨跌幅'
    freq='daily'

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        # 输出市场标杆股
        # 1、均线排列纯多头
        close_badj = get_daily_1factor('close_badj', code_list=self.code_list)
        line5 = close_badj.rolling(5).mean()
        line10 = close_badj.rolling(10).mean()
        line20 = close_badj.rolling(20).mean()
        line30 = close_badj.rolling(30).mean()
        line60 = close_badj.rolling(60).mean()
        line240 = close_badj.rolling(240).mean()
        BenchMarkStock = ((close_badj > line10) & (line5 > line10) & (line10 > line20) & (line20 > line30) & (line30 > line60) & (line60 > line240))
        # 2、涨跌幅
        Max_Pct = close_badj.pct_change(20).rank(pct=True, axis=1)
        PctStock = ((Max_Pct > 0.95) & (Max_Pct > 0.4))
        # 3、涨停数量
        limit_max = get_daily_1factor('limit_max', code_list=self.code_list)
        close = get_daily_1factor('close', code_list=self.code_list)
        Limit_Time = ((limit_max == close).rolling(40).sum() >= 3)
        # 4、市场股票池
        code_list = clean_stock_list(no_ST=True, least_live_days=10, least_recover_days=2)
        # 5、位于最近新高附近
        high_position = (1 - close_badj / close_badj.rolling(120).max() < 0.2)
        TodayBest = (BenchMarkStock.rolling(5).sum() == 5) & Limit_Time & PctStock & code_list
        # 最终结果
        StockChoice = ((TodayBest.rolling(10).max() == True) & high_position).loc[self.cal_date_range,self.code_list]

        stock_pct = get_daily_1factor('pct_chg', self.cal_date_range, self.code_list)
        stock_pct = stock_pct.rolling(5).mean()
        NewStockPct = stock_pct[StockChoice].mean(axis=1)
        NewStockPct = np.array(NewStockPct)[:, np.newaxis].repeat(len(self.code_list), axis=1)

        return NewStockPct


    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return arr_match_index(self.st_factor(), self.cal_date_range, self.date_range)

if __name__=='__main__':
    val1 = cal_factor(numd={})
    val2 = cal_factor(numd={'daily': 10})
    gap = abs(val1 - val2)
    print(np.nansum(gap))
