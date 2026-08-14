from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *

class ConceptDaliyDownLimit(crossFactor):
    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        close = get_daily_1factor('close',self.cal_date_range)
        limit_down = get_daily_1factor('limit_min', self.cal_date_range)

        limitDown_num = (close==limit_down)
        limitDown_num = df_match_index_col(limitDown_num, self.code_list, self.cal_date_range)# np.array

        return limitDown_num

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
    f = ConceptDaliyDownLimit(group='sw1', func='cross_sum',author='tx',extend_days=5,
                              factor_name='ConceptDaliyDownLimit',logic='板块日间跌停数量',freq='daily')
    f.save_result()


