
from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


class xq_min_index_ratio(crossFactor):
    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        close_min = get_minute_1factor('close', self.cal_date_range[0], self.cal_date_range[-1])
        pre_close = get_daily_1factor('pre_close', self.cal_date_range)
        pre_close = pd.DataFrame(pre_close.loc[close_min.index.get_level_values('date')].values,
                                 index=close_min.index, columns=pre_close.columns)
        pct_min = close_min/pre_close-1
        stk_class = pd.DataFrame(index=close_min.index, columns=close_min.columns)
        stk_class.columns = stk_class.columns.map(trans_int2windcode)

        stk_class[stk_class.columns[stk_class.columns.str.endswith('SZ')]] = 1
        stk_class[stk_class.columns[stk_class.columns.str.endswith('SH')]] = 2
        stk_class.columns = stk_class.columns.map(trans_windcode2int)

        pct_min = df_match_index_col(pct_min, self.code_list, self.cal_date_range, '1min')# np.array
        stk_class = df_match_index_col(stk_class, self.code_list, self.cal_date_range, '1min')
        return pct_min, stk_class

    def cal_factor(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        pct_min, stk_class = self.st_factor()
        sz = np.where(stk_class == 1, pct_min, np.nan)
        sz_ratio = index2st(((sz>0).sum(axis=2)/(sz<0).sum(axis=2)).reshape(pct_min.shape[0], pct_min.shape[1], 1), len(self.code_list))
        sh = np.where(stk_class == 2, pct_min, np.nan)
        sh_ratio = index2st(((sh > 0).sum(axis=2) / (sh < 0).sum(axis=2)).reshape(pct_min.shape[0], pct_min.shape[1], 1),len(self.code_list))
        stk_index_ratio = np.where(stk_class == 1, sz_ratio, sh_ratio)
        return arr_match_index(stk_index_ratio, self.cal_date_range, self.date_range)

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
    f = xq_min_index_ratio(group, func, 40, 20170101, 20210531, 'xq', 'xq_min_index_ratio', '对应指数分钟涨跌比',
                             article=None, freq='1min')
    f.save_result()
