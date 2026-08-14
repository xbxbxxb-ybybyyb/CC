
from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


class xq_index_open_pct(crossFactor):
    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        open = get_daily_1factor('open', self.cal_date_range, type='bench')
        pre_close = get_daily_1factor('close', self.cal_date_range, type='bench').shift(1)
        open_pct = open/pre_close - 1
        stk_open = get_daily_1factor('open', self.cal_date_range)
        stk_class = pd.DataFrame(index=stk_open.index, columns=stk_open.columns)
        stk_class.columns = stk_class.columns.map(trans_int2windcode)

        stk_class[stk_class.columns[stk_class.columns.str.endswith('SZ')]] = 1
        stk_class[stk_class.columns[stk_class.columns.str.endswith('SH')]] = 2
        stk_class.columns = stk_class.columns.map(trans_windcode2int)

        index_open_pct = ((stk_class == 1) * (stk_open > 0)).mul(open_pct['SZCZ'], axis=0) + \
                         ((stk_class == 2) * (stk_open > 0)).mul(open_pct['SZZZ'], axis=0)
        index_open_pct = df_match_index_col(index_open_pct, self.code_list, self.cal_date_range)# np.array
        return index_open_pct

    def cal_factor(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        index_open_pct = self.st_factor()
        return arr_match_index(index_open_pct, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_factor()


if __name__ == '__main__':
    group, func = None, None
    print('-------------{}-----------{}-------------'.format(group, func))
    f = xq_index_open_pct(group, func, 40, 20170101, 20210531, 'xq', 'xq_index_open_pct',
                          '对应指数集合竞价涨跌幅', article=None, freq='daily')
    f.save_result()
