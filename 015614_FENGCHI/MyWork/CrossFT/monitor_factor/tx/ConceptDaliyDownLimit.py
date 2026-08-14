from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *

class ConceptDaliyDownLimit(crossFactor):
    cross_group='sw1'
    cross_func='cross_sum'
    author='tx'
    extend_days=5
    logic='板块日间跌停数量'
    freq='daily'

    basic_datas = {'daily': ['close','limit_min']}
    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        close = self.database['daily']['close']
        limit_down = self.database['daily']['limit_min']
        limitDown_num = (close==limit_down)
        return limitDown_num


    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()

if __name__=='__main__':
    f = ConceptDaliyDownLimit()
    f.save_result()