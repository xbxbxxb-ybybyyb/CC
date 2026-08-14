# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : AmtStdCorrClose_5m.py

import sys

# sys.path.extend(['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/EnsembleMonitor', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python', '/data/user/015664/TriggeredTrading/StrongStockModel', '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master', '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic', '/data/user/015664/TriggeredTrading'])


from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossOperators import *


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


class AmtStdCorrClose_5m(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = '自定义'
    extend_days = 2
    author = 'lzc'
    logic = '成交额日内除均值后求波动率，收盘价对日内价标准化，在截面求相关系数*成交额波动率  按昨日 T时刻到今日T时刻为一日计算'
    article = ''
    freq = '5mins'
    basic_datas = {'daily': ['close'], '30mins': [], '5mins': ['amt', 'close'], '1min': []}

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return self.database['daily']['close'], self.database['5mins']['amt'], self.database['5mins']['close']

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        _, amt, close_min = self.st_factor()
        shape = close_min.shape
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

        amt = np.where(np.isfinite(amt), amt, 0)
        close_finit = np.isfinite(close_min)
        close_min = np.where(close_finit, close_min, 0)

        amt_recent_day_mean = intrad_past_day_rolling_mean(amt, close_finit)
        amt_std = intrad_past_day_rolling_std(amt - amt_recent_day_mean, close_finit)

        close_m, close_v = intrad_past_day_rolling_mv(close_min, close_finit)

        close_Z = (close_min - close_m) / close_v
        minute_group = sameshape(close_min, self.group_factor())
        print('stage1')

        import gc
        del close_min, amt, close_m, close_v, amt_recent_day_mean
        gc.collect()

        EX = st2groupst(amt_std, minute_group, cross_mean)
        gc.collect()
        print(2)
        EY = st2groupst(close_Z, minute_group, cross_mean)
        gc.collect()
        print(3)
        EXY = st2groupst(close_Z * amt_std, minute_group, cross_mean)
        gc.collect()
        print(1)

        print('stage2')
        group_cov = EXY - EX * EY
        del EX, EY, EXY
        gc.collect()
        print('stage3')

        STDX = st2groupst(amt_std, minute_group, cross_std)
        STDY = st2groupst(close_Z, minute_group, cross_std)

        STDXY = STDX * STDY
        print('stage4')
        del STDY, STDX, close_Z
        gc.collect()

        group_corr = group_cov / STDXY

        return arr_match_index(group_corr * amt_std, self.cal_date_range, self.date_range)

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
    # f = AmtStdCorrClose_5m()
    e = time.time()
    cal_factor()
    # f.result()
    # f.save_result()
    print(f'total calc time {time.time() - e}')
    # send_message(['015664'],f'total calc time {time.time()-e}')
