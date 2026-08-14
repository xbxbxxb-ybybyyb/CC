# coding: utf-8
# Author：fengchi863
# Date ：2021/9/9 10:41

'''
该因子还存在bug未解决
'''

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *


class InfoSpreadSpeed(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 20
    author = 'fc'
    logic = '行业信息传播速度快慢：daily_moment-mean(dailymoment)/std. dailymoment=dailyret/dailyvol'
    article = '技术指标系列报告之五'
    freq = 'daily'
    basic_datas = {'daily': ['volume', 'close_badj', 'a_mkt_cap']}

    def st_factor(self):
        close = self.database['daily']['close_badj']
        a_mkt_cap = self.database['daily']['a_mkt_cap']
        ret = dt_pct(close, 1)

        return ret, a_mkt_cap, dt_std(ret, 10), self.database['daily']['volume']

    def cal_groupst(self):
        ret, a_mkt_cap, stk_std, vol = self.st_factor()
        self.group = sameshape(ret, self.group_factor())

        a_mkt_weight = a_mkt_cap / st2groupst(a_mkt_cap, self.group, cross_sum)
        industry_ret = st2group(a_mkt_weight * ret, self.group, cross_sum)
        industry_vol = st2group(vol, self.group, cross_sum)
        daily_moment = industry_ret / industry_vol
        group_ret = (daily_moment - np.nanmean(daily_moment, axis=-1, keepdims=True)) / \
                    np.nanstd(daily_moment, axis=-1, keepdims=True)
        ret = group2st(self.group, group_ret)
        return ret

    def cal_customst(self):
        ret = self.cal_groupst()
        return arr_match_index(ret, self.cal_date_range, self.date_range)

    def result(self):
        return self.cal_customst()


if __name__ == '__main__':
    f = InfoSpreadSpeed(start=20210401, end=20210501)
    f.result()
    cal_factor()
