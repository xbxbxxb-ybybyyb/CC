from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *

class ConceptMinPct_10(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=5
    author='tx'
    logic='板块行业10分钟涨速'
    freq='1min'

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        stock_close = get_minute_1factor('close', start_datetime=self.cal_start,end_datetime=self.end, code_list=self.code_list)
        stock_pct = stock_close.groupby('date').pct_change(10)
        stock_pct = df_match_index_col(stock_pct, self.code_list, self.cal_date_range, '1min')  # np.array

        return stock_pct

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
        return self.cal_groupst()

if __name__=='__main__':
    f = ConceptMinPct_10()
    f.save_result()