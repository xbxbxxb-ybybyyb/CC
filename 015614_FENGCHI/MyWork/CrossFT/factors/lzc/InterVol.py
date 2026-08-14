# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : InterVol.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


class InterVol(crossFactor):
    cross_group='sw1'
    cross_func='cross_sum'
    extend_days = 20
    author='lzc'
    logic='最高价对收盘价收益率个股标准差对行业标准差'
    article=''
    freq='daily'

    window = 15
    basic_datas = {'daily': ['high', 'close'], '30mins': [], '5mins': [], '1min': []}
    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        high, close = [self.database['daily'][x] for x in ['high', 'close']]
        high_close_ret = high / close - 1
        high_close_ret = pd.DataFrame(high_close_ret[:, 0, :], index=self.cal_date_range, columns=self.code_list)

        # rolling_std = high_close_ret.rolling(self.window).std(ddof=0)
        rolling_ret_sum = high_close_ret.rolling(self.window).sum()
        rolling_ret2_sum = (high_close_ret ** 2).rolling(self.window).sum()
        rolling_count = high_close_ret.rolling(self.window).count()

        return df_match_index_col(rolling_ret_sum, self.code_list, self.cal_date_range), \
               df_match_index_col(rolling_ret2_sum, self.code_list, self.cal_date_range), \
               df_match_index_col(rolling_count, self.code_list, self.cal_date_range)

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        rolling_ret_sum, rolling_ret2_sum, rolling_count = self.st_factor()
        self.group = sameshape(rolling_ret_sum, self.group_factor())

        group_ret_sum = st2groupst(rolling_ret_sum, self.group, cross_sum)
        group_ret2_sum = st2groupst(rolling_ret2_sum, self.group, cross_sum)
        group_count = st2groupst(rolling_count, self.group, cross_sum)
        stk_std = (rolling_ret2_sum / rolling_count - (rolling_ret_sum / rolling_count) ** 2) ** 0.5
        group_std = ((group_ret2_sum / group_count) - (group_ret_sum / group_count) ** 2) ** 0.5

        return arr_match_index(stk_std / group_std, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()



if __name__ == '__main__':
    cal_factor()
