# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : IndustryMarginalCositOfImmediacyAskRollingDaySharpe_5M.py
import sys

sys.path.extend(['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/EnsembleMonitor',
                 '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python', '/data/user/015664/TriggeredTrading/StrongStockModel',
                 '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master',
                 '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic',
                 '/data/user/015664/TriggeredTrading'])

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class IndustryMarginalCositOfImmediacyAskRollingDaySharpe_5M(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = ''
    extend_days = 15
    author = 'lzc'
    logic = '根据逻辑计算个股卖单流动性 并 衍生分组卖单流动性 相乘 滚动一日夏普'
    article = '中信建投	20201023	因子深度研究系列	买卖报单流动性因子构建'
    freq = '5mins'
    basic_datas = {'daily': ['free_float_shares'], '30mins': [], '5mins': ['selltradevol', 'selltradeamt', 'close'], '1min': []}

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return  # self.database['5mins']['close_badj']

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        selltradevol, selltradeamt, close = [self.database['5mins'][x] for x in ['selltradevol', 'selltradeamt', 'close']]
        free_float_shares = self.database['daily']['free_float_shares']
        free_float_shares = delay(free_float_shares, 1)
        daily_group = sameshape(free_float_shares, self.group_factor())
        minute_group = sameshape(selltradevol, self.group_factor())

        sell_vwap = selltradeamt / selltradevol
        sell_order_amt_group = st2groupst(selltradeamt, minute_group, cross_sum)
        industry_sell_vwap = sell_order_amt_group / st2groupst(selltradevol, minute_group, cross_sum)
        IndutryPrice = st2groupst(close * free_float_shares, minute_group, cross_sum)
        VWAPMA_stk = sell_vwap / close - 1
        VWAPMA_group = industry_sell_vwap / IndutryPrice - 1
        MCIA_stk = VWAPMA_stk / selltradeamt
        MCIA_group = VWAPMA_group / sell_order_amt_group

        # return arr_match_index(np.nanmean(MCIA_stk, axis=1)[:, None, :] * np.nanmean(MCIA_group, axis=1)[:, None, :],
        #                        self.cal_date_range, self.date_range)
        import bottleneck
        def intrad_past_day_rolling_sum(x_, finit=None):
            shape = x_.shape
            if finit is None:
                finit = np.isfinite(x_)
            x = np.where(finit, x_, 0)
            return bottleneck.move_sum(np.concatenate([delay(x, 1), x], axis=1), window=shape[1], axis=1)[:, -shape[1]:, :]

        def intrad_past_day_rolling_mv(x, finit=None):
            if finit is None:
                finit = np.isfinite(x)
            SUM = intrad_past_day_rolling_sum(np.where(finit, x, 0))
            SUM2 = intrad_past_day_rolling_sum(np.where(finit, x ** 2, 0))
            COUNT = intrad_past_day_rolling_sum(finit)
            return SUM / COUNT, (SUM2 / COUNT - (SUM / COUNT) ** 2) ** 0.5

        mean_stk, std_stk = intrad_past_day_rolling_mv(MCIA_stk)
        mean_group, std_group = intrad_past_day_rolling_mv(MCIA_group)

        stk_factor = (MCIA_stk - mean_stk) / std_stk
        group_factor = (MCIA_group - mean_group) / std_group

        return arr_match_index(stk_factor * group_factor, self.cal_date_range, self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()


if __name__ == '__main__':
    cal_factor()
