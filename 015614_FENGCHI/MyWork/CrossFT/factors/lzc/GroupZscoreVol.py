# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : GroupZscoreVol.py


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *
from basic.operators import *

class GroupZscoreVol(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 16
    author = 'lzc'
    logic = '个股近期波动率组内zscore*分组指数波动率'
    article = '招商证券	20200618	琢璞系列报告017'
    freq = 'daily'
    basic_datas = {'daily': ['close_badj', 'a_mkt_cap'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        close, a_mkt_cap = [self.database['daily'][x] for x in ['close_badj', 'a_mkt_cap']]
        ret = dt_delay(close, 1)

        return ret, a_mkt_cap, dt_std(ret, self.extend_days - 1)

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        ret, a_mkt_cap, stk_std = self.st_factor()
        self.group = sameshape(ret, self.group_factor())

        a_mkt_weight = a_mkt_cap / st2groupst(a_mkt_cap, self.group, cross_sum)
        industry_ret = st2groupst(a_mkt_weight * ret, self.group, cross_sum)
        industry_std = pd.DataFrame(industry_ret[:, 0, :]).rolling(self.window).std().values[:, None, :]
        stk_zscor = (stk_std - st2groupst(stk_std, self.group, cross_mean)) / st2groupst(stk_std, self.group, cross_std)

        return arr_match_index(stk_zscor * industry_std, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    cal_factor()
