
from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


class xq_trend_stk_pct(crossFactor):
    cross_group='ones'
    cross_func='cross_mean'
    extend_days=150
    author='xq'
    logic='趋势股平均涨跌幅'
    article=None
    freq='daily'


    def avg_score(self, close, n):
        pre = close
        stat = pd.DataFrame(0, index=close.index, columns=close.columns)
        for i in range(1, n + 1):
            cur = close.rolling(i).mean()
            stat += (pre > cur).applymap(lambda x: 100 if x else 0)
            pre = cur

        stat /= n
        return stat

    def avg_distance(self, close, n):
        pre = close
        dis = pd.DataFrame(0, index=close.index, columns=close.columns)
        for i in range(1, n + 1):
            cur = close.rolling(i).mean()
            dis += abs(pre - cur) / pre
            pre = cur
        return dis

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        close = get_daily_1factor('close',self.cal_date_range)
        pct = get_daily_1factor('pct_chg', self.cal_date_range)
        ma5 = close.rolling(5).mean()
        ma20 = close.rolling(20).mean()
        ma60 = close.rolling(60).mean()
        score_120 = self.avg_score(close, 120)
        score_60 = self.avg_score(close, 60)
        dis_60 = self.avg_distance(close, 60)
        trend_stk = (ma5 > ma20) & (ma20 > ma60) & (close > ma20) & (dis_60 > 0.2) & (score_60 > 60) & (score_120 > 60)
        trend_stk = df_match_index_col(trend_stk.shift(1), self.code_list, self.cal_date_range)
        pct = df_match_index_col(pct, self.code_list, self.cal_date_range)
        return pct, trend_stk

    def cal_groupst(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        pct, trend_stk = self.st_factor()
        self.group = sameshape(trend_stk, self.group_factor())
        trend_pct = np.where(trend_stk == 1, pct, np.nan)
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
    f = xq_trend_stk_pct()
    f.save_result()