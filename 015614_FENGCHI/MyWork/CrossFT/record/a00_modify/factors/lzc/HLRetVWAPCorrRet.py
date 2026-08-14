# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : HLRetVWAPCorrRet.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


class HLRetVWAPCorrRet(crossFactor):
    cross_group='sw1'
    cross_func='cross_sum'
    extend_days=0
    author='lzc'
    logic='High减去Low除以Close，与Vwap的组内相关系数，再乘与High减去Low除以Close'
    article=''
    freq='daily'

    window = 15

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        high = get_daily_1factor('high')
        low = get_daily_1factor('low')
        close = get_daily_1factor('close')
        vol = get_daily_1factor('volume')
        amt = get_daily_1factor('amt') * 10
        diff_ret = (high - low) / close
        vwap = amt / vol

        return df_match_index_col(diff_ret, self.code_list, self.cal_date_range), \
               df_match_index_col(vwap, self.code_list, self.cal_date_range)

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        diff_ret, vwap = self.st_factor()
        self.group = sameshape(diff_ret, self.group_factor())

        EXY_EXEY = st2groupst(diff_ret * vwap, self.group, cross_mean) - st2groupst(vwap, self.group, cross_mean) * st2groupst(diff_ret, self.group, cross_mean)
        STDXSTDY = st2groupst(diff_ret, self.group, cross_std) * st2groupst(vwap, self.group, cross_std)
        group_corr = EXY_EXEY / STDXSTDY
        return arr_match_index(group_corr * diff_ret, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    f = HLRetVWAPCorrRet()
    f.save_result()