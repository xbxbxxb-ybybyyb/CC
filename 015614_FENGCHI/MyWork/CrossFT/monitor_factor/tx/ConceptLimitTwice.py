from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *

class ConceptLimitTwice(crossFactor):
    cross_group='sw1'
    cross_func='cross_sum'
    extend_days=5
    author='tx'
    logic='板块日内连板数量'
    freq='1min'

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        stock_close = get_minute_1factor('close', start_datetime=self.cal_start,end_datetime=self.end, code_list=self.code_list)
        limit_max = get_daily_1factor('limit_max',self.cal_date_range,code_list=self.code_list)
        limit_max_min = pd.DataFrame(np.array(limit_max.loc[stock_close.index.get_level_values('date')]), index=stock_close.index,columns=stock_close.columns)
        limit_min_num = (stock_close==limit_max_min)
        # 日频数据
        daily_close = get_daily_1factor('close', self.cal_date_range, code_list=self.code_list)
        IfLimit = (daily_close  == limit_max).shift(1)
        IfLimit.fillna(False,inplace=True)
        IfLimit_min = pd.DataFrame(np.array(IfLimit.loc[stock_close.index.get_level_values('date')]),index=stock_close.index, columns=stock_close.columns)

        double_num = (IfLimit_min & limit_min_num)
        double_num = df_match_index_col(double_num, self.code_list, self.cal_date_range, '1min')  # np.array

        return double_num

    def cal_groupst(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        self.factor =  self.st_factor()
        self.group = sameshape(self.factor, self.group_factor())

        #def cal_mean(x,axis):
        #    return np.nansum(x,axis)

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
    f = ConceptLimitTwice()
    f.save_result()