# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : VolPriceInterCorr.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


class VolPriceInterCorr(crossFactor):
    window = 15

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        vol = get_daily_1factor('volume')
        close = get_daily_1factor('close')
        EX = vol.rolling(self.window).mean()
        EY = close.rolling(self.window).mean()
        EXY = (close * vol).rolling(self.window).mean()
        STDX = vol.rolling(self.window).std()
        STDY = close.rolling(self.window).std()
        factor = (EXY - EX * EY) / (STDX * STDY)
        return df_match_index_col(factor, self.code_list, self.cal_date_range)

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        self.factor = self.st_factor()
        self.group = sameshape(self.factor, self.group_factor())

        group_mean = st2groupst(self.factor, self.group, cross_mean)
        group_std = st2groupst(self.factor, self.group, cross_std)
        factor = (self.factor - group_mean) / group_std
        return arr_match_index(factor, self.cal_date_range, self.date_range)

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
    f = VolPriceInterCorr('sw1', 'cross_sum', 0, 20170101, 20210531, author='lzc', factor_name='VolPriceInterCorr', logic='最高价对收盘价收益率个股标准差对行业标准差', \
                          article='', freq='daily')
    e = time.time()
    f.save_result()
    print(f'total calc time {time.time() - e}')
    # send_message(['015664'],f'total calc time {time.time()-e}')
