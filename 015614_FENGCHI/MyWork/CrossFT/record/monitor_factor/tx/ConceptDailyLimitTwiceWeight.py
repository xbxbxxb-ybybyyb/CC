from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *

class ConceptDailyLimitTwiceWeight(crossFactor):
    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        close = get_daily_1factor('close', self.cal_date_range)
        limit_down = get_daily_1factor('limit_max', self.cal_date_range)

        limitDown_num = (close == limit_down)
        limitTwice = limitDown_num.rolling(2).sum() == 2
        limitTwice = df_match_index_col(limitTwice, self.code_list, self.cal_date_range)  # np.array

        Stock_num = (close >0)
        Stock_num = df_match_index_col(Stock_num, self.code_list, self.cal_date_range)  # np.array

        return limitTwice,Stock_num

    def cal_groupst(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        self.factor1,self.factor2 =  self.st_factor()
        self.group = sameshape(self.factor1, self.group_factor())

        #def cal_mean(x,axis):
        #    return np.nansum(x,axis)

        self.func = self.group_func()
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
    f = ConceptDailyLimitTwiceWeight(group='sw1', func='cross_sum',author='tx',extend_days=5,
                              factor_name='ConceptDailyLimitTwiceWeight',logic='板块日间连板数量占比',freq='daily')
    f.save_result()



