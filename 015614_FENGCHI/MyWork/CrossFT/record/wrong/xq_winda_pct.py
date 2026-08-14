
from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *
from xquant.factordata import FactorData
s = FactorData()


class xq_winda_pct(crossFactor):
    cross_group=None
    cross_func=None
    extend_days=40
    author='xq'
    logic='wind全a单边涨跌幅'
    article=None
    freq='daily'

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        winda = s.get_factor_value('WIND_AIndexWindIndustriesEOD', s_info_windcode='881001.WI',
                                   factors=['trade_dt', 's_dq_pctchange'],
                                   trade_dt=['>='+str(self.cal_date_range[0]), '<='+str(self.cal_date_range[-1])])
        winda = winda.set_index('TRADE_DT').sort_index()
        return winda

    def cal_factor(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        winda = self.st_factor()
        factor = np.repeat(winda.values, len(self.code_list)).reshape(winda.shape[0], 1, len(self.code_list))
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_factor()

if __name__=='__main__':
    val2 = cal_factor(numd={'daily': 15})