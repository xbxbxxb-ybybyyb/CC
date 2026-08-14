# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : GroupSelfCorr_5m.py
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


class GroupSelfCorr_5m(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 15
    author = 'lzc'
    logic = '个股收益在组内的zscore的自相关性  按昨日T时刻到今日T时刻为一日计算'
    article = ''
    freq = '5mins'
    basic_datas = {'daily': [], '30mins': [], '5mins': ['close_badj'], '1min': []}

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return self.database['5mins']['close_badj']

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        close_badj = self.st_factor()
        close_badj = close_badj.swapaxes(0, 1)
        ret = close_badj / delay(close_badj) - 1
        ret = ret.swapaxes(0, 1)
        shape = ret.shape
        import bottleneck
        intrad_past_day_rolling_sum = lambda x: bottleneck.move_sum(np.concatenate([delay(x, 1), x], axis=1), window=shape[1], axis=1)[:, -shape[1]:, :]

        def intrad_past_day_rolling_mean(x, finit):
            SUM = intrad_past_day_rolling_sum(np.where(finit, x, 0))
            COUNT = intrad_past_day_rolling_sum(finit)
            return SUM / COUNT

        def intrad_past_day_rolling_std(x, finit):
            SUM = intrad_past_day_rolling_sum(np.where(finit, x, 0))
            SUM2 = intrad_past_day_rolling_sum(np.where(finit, x ** 2, 0))
            COUNT = intrad_past_day_rolling_sum(finit)
            return SUM2 / COUNT - (SUM / COUNT) ** 2

        def intrad_past_day_rolling_mv(x, finit):
            SUM = intrad_past_day_rolling_sum(np.where(finit, x, 0))
            SUM2 = intrad_past_day_rolling_sum(np.where(finit, x ** 2, 0))
            COUNT = intrad_past_day_rolling_sum(finit)
            return SUM / COUNT, SUM2 / COUNT - (SUM / COUNT) ** 2


        self.group = sameshape(ret, self.group_factor())
        grou_zscore = (ret - st2groupst(ret, self.group, cross_mean)) / st2groupst(ret, self.group, cross_std)
        grou_zscore_lag = delay(grou_zscore.swapaxes(0, 1)).swapaxes(0, 1)

        both_finit = np.isfinite(grou_zscore) & np.isfinite(grou_zscore_lag)

        EXY = intrad_past_day_rolling_mean(grou_zscore_lag * grou_zscore, both_finit)
        EXEY = intrad_past_day_rolling_mean(grou_zscore, both_finit) * intrad_past_day_rolling_mean(grou_zscore_lag, both_finit)
        STDXSTDY = intrad_past_day_rolling_std(grou_zscore, both_finit) * intrad_past_day_rolling_std(grou_zscore_lag, both_finit)

        corr = (EXY - EXEY) / STDXSTDY

        return arr_match_index(corr, self.cal_date_range, self.date_range)

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
    # f = GroupSelfCorr()
    e = time.time()
    # f.result()
    # f.save_result()
    cal_factor()
    print(f'total calc time {time.time() - e}')
    # send_message(['015664'],f'total calc time {time.time()-e}')
