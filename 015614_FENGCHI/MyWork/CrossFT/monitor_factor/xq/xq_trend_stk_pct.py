
from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *
from basic.operators import *

class xq_trend_stk_pct(crossFactor):
    cross_group='ones'
    cross_func='cross_mean'
    extend_days = 150
    author='xq'
    logic='趋势股平均涨跌幅'
    article=None
    freq='daily'

    basic_datas = {'daily': ['close', 'pct_chg']}
    def avg_score(self, close, n):
        pre = np.array(close)
        stat = np.zeros_like(close)
        for i in range(1, n + 1):
            cur = dt_mean(close, i)
            stat += np.where(pre > cur, 100, 0)
            pre = cur
        stat /= n
        return stat

    def avg_distance(self, close, n):
        pre = np.array(close)
        dis = np.zeros_like(close)
        for i in range(1, n + 1):
            cur = dt_mean(close, i)
            dis += abs(pre - cur) / pre
            pre = cur
        return dis

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        close = self.database['daily']['close']
        pct = self.database['daily']['pct_chg']
        ma5 = dt_mean(close, 5)
        ma20 = dt_mean(close, 20)
        ma60 = dt_mean(close, 60)
        score_120 = self.avg_score(close, 120)
        score_60 = self.avg_score(close, 60)
        dis_60 = self.avg_distance(close, 60)
        trend_stk = (ma5 > ma20) & (ma20 > ma60) & (close > ma20) & (dis_60 > 0.2) & (score_60 > 60) & (score_120 > 60)
        trend_stk = dt_delay(trend_stk.astype(int),1)
        trend_stk_pct = np.nanmean(np.where(trend_stk==0,np.nan,trend_stk) * pct, axis=-1)
        return trend_stk_pct

    def cal_factor_value(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        trend_stk_pct = self.st_factor()
        factor = np.repeat(trend_stk_pct, len(self.code_list)).reshape(trend_stk_pct.shape[0], 1, len(self.code_list))
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_factor_value()


if __name__ == '__main__':
   val1 = cal_factor(numd={})
   val2 = cal_factor(numd={'daily':10})
   print(np.nansum(abs(val1-val2)))