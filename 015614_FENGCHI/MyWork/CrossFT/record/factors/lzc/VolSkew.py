# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : VolKurt.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


class VolSkew(crossFactor):

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        vol = get_minute_1factor('vol', start_datetime=self.cal_start, end_datetime=self.end)
        vol = df_match_index_col(vol, self.code_list, self.cal_date_range, freq='1min')
        return vol

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        vol = self.st_factor()
        # vol = np.where(np.isnan(vol),0,vol)
        group_min = sameshape(vol, self.group_factor())
        group_vol_sum = st2groupst(vol, group_min, cross_sum)

        skew_stk = np.nanmean((vol.swapaxes(0, 1) - np.nanmean(vol, axis=1)) ** 3, axis=0)
        skew_group = np.nanmean((group_vol_sum.swapaxes(0, 1) - np.nanmean(group_vol_sum, axis=1)) ** 3, axis=0)

        group_day = sameshape(skew_stk, self.group_factor())
        skew_stk_zscore = (skew_stk - st2groupst(skew_stk, group_day, cross_mean)) / st2groupst(skew_stk, group_day, cross_std)

        return arr_match_index(skew_stk_zscore * skew_group, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    # for group in groups:
    #     for func in funcs:
    #         print('-------------{}-----------{}-------------'.format(group,func))
    f = VolSkew('sw1', 'cross_sum', 0, 20170101, 20210531, author='lzc', factor_name='VolSkew', logic='个股日内成交量偏度组内zscore*分组成交量偏度', \
                article='', freq='daily')
    e = time.time()
    # f.result()
    f.save_result()
    print(f'total calc time {time.time() - e}')
    # send_message(['015664'],f'total calc time {time.time()-e}')
