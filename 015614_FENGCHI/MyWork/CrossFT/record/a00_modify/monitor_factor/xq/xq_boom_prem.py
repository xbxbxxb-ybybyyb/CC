
from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *



class xq_boom_prem(crossFactor):
    cross_group='ones'
    cross_func='cross_mean'
    extend_days=40
    author='xq'
    logic='炸板溢价'
    article=None
    freq='daily'

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        close = get_daily_1factor('close', self.cal_date_range)
        high = get_daily_1factor('high', self.cal_date_range)
        limit_max = get_daily_1factor('limit_max', self.cal_date_range)
        boom = ((high == limit_max) & (close != limit_max)).shift(1)
        pct = get_daily_1factor('pct_chg', self.cal_date_range)

        boom = df_match_index_col(boom, self.code_list, self.cal_date_range)
        pct = df_match_index_col(pct, self.code_list, self.cal_date_range)
        return boom, pct

    def cal_groupst(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        boom, pct = self.st_factor()
        boom_prem = np.where(boom == 1, pct, np.nan)
        self.group = sameshape(boom, self.group_factor())
        factor = st2groupst(boom_prem, self.group, self.group_func())
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    f = xq_boom_prem()
    f.save_result()