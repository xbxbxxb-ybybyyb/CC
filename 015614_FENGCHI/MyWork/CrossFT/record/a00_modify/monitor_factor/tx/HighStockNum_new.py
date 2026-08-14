from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *

class HighStockNum(crossFactor):
    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        # 输出3板及以上个股
        close = get_daily_1factor('close', self.cal_date_range, self.code_list)
        limit_max = get_daily_1factor('limit_max', self.cal_date_range, self.code_list)
        Limit_stock = (close == limit_max)

        stock_pool = clean_stock_list(no_ST=True, least_live_days=10, no_pause=True, least_recover_days=0).loc[self.start:self.end]

        HighStock = ((Limit_stock.rolling(3).sum()==3) & (stock_pool==True)).sum(axis=1)

        HighStock = np.array(HighStock)[:, np.newaxis].repeat(len(self.code_list), axis=1)

        return HighStock

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
        return arr_match_index(self.st_factor(), self.cal_date_range, self.date_range)

if __name__=='__main__':
    f = HighStockNum(group='sw1', func='cross_sum',author='tx',extend_days=10,
                              factor_name='HighStockNum',logic='3板及以上个股数量',freq='daily')
    f.save_result()






