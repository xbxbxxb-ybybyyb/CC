from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *

class ConceptPctRank(crossFactor):
    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        stock_pct = get_daily_1factor('pct_chg',self.cal_date_range)
        stock_pct = df_match_index_col(stock_pct, self.code_list, self.cal_date_range)# np.array

        return stock_pct

    def cal_groupst(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        self.factor =  self.st_factor()
        self.group = sameshape(self.factor, self.group_factor())
        # 自己写一下函数 #
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
        factor_before = self.cal_groupst()
        factor = pd.DataFrame(factor_before[:,0,:],index=self.date_range,columns=self.code_list)
        factor.rank(pct=True,axis=0)
        factor = df_match_index_col(factor, self.code_list, self.date_range)  # np.array

        return factor

if __name__=='__main__':
    f = ConceptPctRank(group='sw1', func='cross_mean',extend_days=5,author='tx',factor_name='ConceptPctRank',logic='板块行业涨跌幅排序',freq='daily')
    f.save_result()
