
from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *



class xq_limitup_num(crossFactor):
    cross_group='ones'
    cross_func='cross_sum'
    extend_days=40
    author='xq'
    logic='全市场涨停家数'
    article=None
    freq='daily'

    basic_datas = {'daily': ['limit_up']}

    def st_factor(self):
        return self.database['daily']['limit_up']

    def cal_groupst(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        limitup = self.st_factor()
        self.group = sameshape(limitup, self.group_factor())
        factor = st2groupst(limitup, self.group, self.group_func())
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    f = xq_limitup_num()
    f.save_result()