# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : MorningAfternoonAmtRatio.py

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


class MorningAfternoonAmtRatio(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 15
    author = 'lzc'
    logic = '上午成额与下午成交额之比近15日的mean/std  *  分组的该值'
    article = '中信建投	20201023	因子深度研究系列	买卖报单流动性因子构建'
    freq = 'daily'
    basic_datas = {'daily': ['amt'], '30mins': [], '5mins': ['amt'], '1min': []}

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''

        return  # self.database['daily']['close_badj'], self.database['daily']['free_float_shares'], self.database['daily']['amt']

    def cal_groupst(self):
        '''
        :return: np.array,个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        # high,low = [self.database['daily'][x] for x in ['high','low']]
        amt, = [self.database['5mins'][x].swapaxes(0, 1) for x in ['amt']]

        morning_amt = np.nansum(amt[:amt.shape[0] // 2, :, :], axis=0)[:, None, :]
        afternoon_amt = np.nansum(amt[amt.shape[0] // 2:, :, :], axis=0)[:, None, :]
        daily_group = sameshape(self.database['5mins']['amt'], self.group_factor())

        stk_ratio = morning_amt / afternoon_amt
        group_ratio = st2groupst(morning_amt, daily_group, cross_sum) / st2groupst(afternoon_amt, daily_group, cross_sum)

        stk_ratio = pd.DataFrame(stk_ratio[:, 0, :])
        group_ratio = pd.DataFrame(group_ratio[:, 0, :])

        stk_sharpe = stk_ratio.rolling(self.window).mean() / stk_ratio.rolling(self.window).std()
        group_sharpe = group_ratio.rolling(self.window).mean() / group_ratio.rolling(self.window).std()

        return arr_match_index(stk_sharpe.values[:, None, :] * group_sharpe.values[:, None, :], self.cal_date_range, self.date_range)

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
    f = MorningAfternoonAmtRatio()
    e = time.time()
    # f.result()
    f.save_result()
    print(f'total calc time {time.time() - e}')
    # send_message(['015664'],f'total calc time {time.time()-e}')
