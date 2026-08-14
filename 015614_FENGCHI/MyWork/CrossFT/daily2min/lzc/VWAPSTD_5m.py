# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : VWAPSTD.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


class VWAPSTD_5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_sum'
    extend_days=5
    author='lzc'
    logic = '个股VWAP对分组VWAP的收益'
    article=''
    freq = '5mins'

    window = 5

    basic_datas = {'5mins': ['vol', 'amt']}
    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        vol = self.database['5mins']['vol']
        amt = self.database['5mins']['amt'] * 10
        # rolling_std = high_close_ret.rolling(self.window).std(ddof=0)
        return vol, amt


    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        vol, amt = self.st_factor()
        self.group = sameshape(vol, self.group_factor())

        group_vol = st2groupst(vol, self.group, cross_sum)
        group_amt = st2groupst(amt, self.group, cross_sum)
        stk_vwap = amt / vol
        group_vwap = group_amt / group_vol

        vwap_ret = stk_vwap / group_vwap - 1
        # factor =

        return arr_match_index(vwap_ret, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()



if __name__ == '__main__':
    val1 = cal_factor()
    # f = VWAPSTD()
    # print(np.nansum(val1.astype(np.float32)-f.result().astype('float32')))
