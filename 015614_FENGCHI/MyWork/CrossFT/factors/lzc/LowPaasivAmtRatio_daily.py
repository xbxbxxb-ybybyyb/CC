# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : LowPaasivAmtRatio.py
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
import gc


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class LowPaasivAmtRatio_daily(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = ''
    extend_days = 15
    author = 'lzc'
    logic = '缩量过程中新增被动委托额被动委托额的比例 滚动240分钟'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': ['a_mkt_cap'], '30mins': [], '5mins': ['passivesellorderamt', 'passivebuyorderamt', 'amt'], '1min': []}

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
        passivesellorderamt, passivebuyorderamt, amt = [self.database['5mins'][x] for x in
                                                        ['passivesellorderamt', 'passivebuyorderamt', 'amt']]
        a_mkt_cap = self.database['daily']['a_mkt_cap']
        a_mkt_cap = delay(a_mkt_cap, 1)
        daily_group = sameshape(a_mkt_cap, self.group_factor())
        minute_group = sameshape(amt, self.group_factor())

        heavy_flag = amt / delay(amt) - 1

        import bottleneck
        def intrad_past_day_rolling_sum(x_, finit=None):
            shape = x_.shape
            if finit is None:
                finit = np.isfinite(x_)
            x = np.where(finit, x_, 0)
            return bottleneck.move_sum(np.concatenate([delay(x, 1), x], axis=1), window=shape[1], axis=1)[:, -shape[1]:, :]

        up = heavy_flag > 0
        down = heavy_flag < 0
        activeamt = passivesellorderamt + passivebuyorderamt
        heavy_activeamt = intrad_past_day_rolling_sum(activeamt, down)
        amt_rolling = intrad_past_day_rolling_sum(activeamt, up)
        factor = heavy_activeamt / amt_rolling
        return arr_match_index(factor[:, [-1], :], self.cal_date_range, self.date_range)

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
    cal_factor()
