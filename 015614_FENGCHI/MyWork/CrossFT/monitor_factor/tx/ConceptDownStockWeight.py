from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *

class ConceptDownStockWeight(crossFactor):
    cross_group='sw1'
    cross_func='cross_sum'
    extend_days=1
    author='tx'
    logic='板块日内下跌占比'
    freq='1min'

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        stock_close = get_minute_1factor('close', start_datetime=self.cal_start, end_datetime=self.end,
                                         code_list=self.code_list)
        pre_close = get_daily_1factor('pre_close', self.cal_date_range, code_list=self.code_list)
        pre_close_min = pd.DataFrame(np.array(pre_close.loc[stock_close.index.get_level_values('date')]),
                                     index=stock_close.index, columns=stock_close.columns)
        stock_pct = stock_close / pre_close_min - 1
        up_num = (stock_pct<0)
        up_num = df_match_index_col(up_num, self.code_list, self.cal_date_range, '1min')  # np.array

        stock_num = (stock_close>0)
        stock_num = df_match_index_col(stock_num, self.code_list, self.cal_date_range, '1min')  # np.array

        return up_num,stock_num

    def cal_groupst(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        self.factor1,self.factor2 =  self.st_factor()
        #def cal_mean(x,axis):
        #    return np.nansum(x,axis)
        self.func = self.group_func()
        self.group = sameshape(self.factor1, self.group_factor())

        res1 = st2groupst(self.factor1, self.group, self.func)
        res2 = st2groupst(self.factor2, self.group, self.func)
        res = res1/res2

        return arr_match_index(res,self.cal_date_range,self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()

if __name__=='__main__':
    f = ConceptDownStockWeight()
    f.save_result()