
from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *
import bottleneck as bn
from basic.operators import *

class xq_min_trend_stk_pct(crossFactor):
    cross_group='ones'
    cross_func='cross_mean'
    extend_days=150
    author='xq'
    logic='分钟趋势股平均涨跌幅'
    article=None
    freq='1min'
    basic_datas = {'daily':['close','pre_close'],'1min': ['close']}
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
        ma5 = dt_mean(close, 5)
        ma20 = dt_mean(close, 20)
        ma60 = dt_mean(close, 60)
        score_120 = self.avg_score(close, 120)
        score_60 = self.avg_score(close, 60)
        dis_60 = self.avg_distance(close, 60)
        trend_stk = dt_delay((ma5 > ma20) & (ma20 > ma60) & (close > ma20) & (dis_60 > 0.2) & (score_60 > 60) & (score_120 > 60),1)
        # trend_stk = pd.DataFrame(trend_stk, index=close.index, columns=close.columns)
        # trend_stk = df_match_index_col(trend_stk.shift(1), self.code_list, self.cal_date_range)
        close_min = self.database['1min']['close']#get_minute_1factor('close', self.cal_date_range[0], self.cal_date_range[-1])
        pre_close = self.database['daily']['pre_close']#get_daily_1factor('pre_close', self.cal_date_range)
        # pre_close = pd.DataFrame(pre_close.loc[close_min.index.get_level_values('date')].values,
        #                          index=close_min.index, columns=pre_close.columns)
        pct_min = close_min / pre_close - 1
        #pct_min = df_match_index_col(pct_min, self.code_list, self.cal_date_range, '1min')
        return pct_min, trend_stk

    def cal_groupst(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        pct_min, trend_stk = self.st_factor()
        trend_stk = np.repeat(trend_stk, pct_min.shape[1], axis=1)
        self.group = sameshape(trend_stk, self.group_factor())
        trend_pct = np.where(trend_stk == 1, pct_min, np.nan)
        factor = st2groupst(trend_pct, self.group, self.group_func())
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    val1 = cal_factor( onlycheck=True)
