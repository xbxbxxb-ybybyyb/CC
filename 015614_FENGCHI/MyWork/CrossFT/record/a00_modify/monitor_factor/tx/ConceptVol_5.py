from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *

class ConceptVol_5(crossFactor):
    cross_group='sw1'
    cross_func='cross_sum'
    extend_days=10
    author='tx'
    logic='板块行业量比5/10'
    freq='daily'

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        amt = get_daily_1factor('amt',self.cal_date_range)
        amt = df_match_index_col(amt, self.code_list, self.cal_date_range)# np.array

        return amt

    def cal_groupst(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        self.factor =  self.st_factor()
        self.group = sameshape(self.factor, self.group_factor())
        # 自己写一下函数 #
        #def cal_mean(x,axis):
        #    return np.nansum(x,axis)

        self.func = self.group_func()
        res = st2groupst(self.factor, self.group, self.func)
        return res

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        factor_before = self.cal_groupst()
        factor = pd.DataFrame(factor_before[:,0,:],index=self.cal_date_range,columns=self.code_list)
        factor = factor.rolling(5).mean()/factor.rolling(10).mean()
        factor = df_match_index_col(factor, self.code_list, self.cal_date_range)  # np.array

        return arr_match_index(factor,self.cal_date_range,self.date_range)

if __name__=='__main__':
    f = ConceptVol_5()
    f.save_result()