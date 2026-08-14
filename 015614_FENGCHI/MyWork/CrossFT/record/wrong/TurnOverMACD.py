# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : TurnOverMACD.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *
import talib


class TurnOverMACD(crossFactor):
    cross_group='sw1'
    cross_func='cross_sum'
    extend_days=40
    author='lzc'
    logic='个股换手率MACD行业内ZSCORE/行业换手率'
    article='中信证券量化投资系列研究行业指数价量联动关系分析与应用'
    freq='daily'

    window = 15

    start = 20150109
    end = 20151231

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        vol = get_daily_1factor('volume')
        free_float_shares = get_daily_1factor('free_float_shares')
        return df_match_index_col(vol, self.code_list, self.cal_date_range), \
               df_match_index_col(free_float_shares, self.code_list, self.cal_date_range)

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        vol, free_float_shares = self.st_factor()
        self.group = sameshape(vol, self.group_factor())

        group_vol = st2groupst(vol, self.group, cross_sum)
        group_free_float_share = st2groupst(free_float_shares, self.group, cross_sum)
        group_turnover = group_vol / group_free_float_share

        stk_turnover = vol / free_float_shares
        stk_turnover = np.where(np.isnan(stk_turnover), 0, stk_turnover)
        group_turnover = np.where(np.isnan(group_turnover), 0, group_turnover)
        macd = np.concatenate(tuple([talib.MACD(stk_turnover[:, 0, i])[0][:, None] for i in range(stk_turnover.shape[-1])]), axis=1)[:, None, :]
        maxd_group = np.concatenate(tuple([talib.MACD(group_turnover[:, 0, i])[0][:, None] for i in range(group_turnover.shape[-1])]), axis=1)[:, None, :]
        stk_zscore = (macd - st2groupst(macd, self.group, cross_mean)) / st2groupst(macd, self.group, cross_std)
        factor = stk_zscore * maxd_group
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    f = TurnOverMACD()
    val = f.result()
    e = time.time()
    val1 = cal_factor(numd={})
    val2 = cal_factor(numd={'daily': 10})
    diff = val1 - val2
    print(f'total calc time {time.time() - e}')
