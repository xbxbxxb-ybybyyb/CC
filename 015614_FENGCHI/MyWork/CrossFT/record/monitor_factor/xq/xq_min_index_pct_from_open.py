
from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


class xq_min_index_pct_from_open(crossFactor):
    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        close_min = get_minute_1factor('close', self.cal_date_range[0], self.cal_date_range[-1],
                                       type='bench', base_date=20100101)
        open = get_daily_1factor('open', self.cal_date_range, type='bench')
        open = pd.DataFrame(open.loc[close_min.index.get_level_values('date')].values,
                            index=close_min.index, columns=open.columns)
        open_pct = close_min/open - 1
        high = get_minute_1factor('high', self.cal_date_range[0], self.cal_date_range[-1])
        stk_class = pd.DataFrame(index=high.index, columns=high.columns)
        stk_class.columns = stk_class.columns.map(trans_int2windcode)

        stk_class[stk_class.columns[stk_class.columns.str.endswith('SZ')]] = 1
        stk_class[stk_class.columns[stk_class.columns.str.endswith('SH')]] = 2
        stk_class.columns = stk_class.columns.map(trans_windcode2int)

        stk_index_pct = ((stk_class == 1) * (high > 0)).mul(open_pct['SZCZ'], axis=0) + \
                        ((stk_class == 2) * (high > 0)).mul(open_pct['SZZZ'], axis=0)
        stk_index_pct = df_match_index_col(stk_index_pct, self.code_list, self.cal_date_range, '1min')# np.array
        return stk_index_pct

    def cal_factor(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        stk_index_pct = self.st_factor()
        return arr_match_index(stk_index_pct, self.cal_date_range, self.date_range)

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
    f = xq_min_index_pct_from_open(group, func, 40, 20170101, 20210531, 'xq', 'xq_min_index_pct_from_open',
                                   '对应指数分钟开盘至今涨跌幅', article=None, freq='1min')
    f.save_result()
