# @Time : 2021/8/16 15:31
# @Author : Zhichen Lu
# @File : IMB_Active_Passive_Price.py
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


class IMB_Active_Passive_Price(crossFactor):
    window = 15
    cross_group = 'sw1'
    cross_func = ''
    extend_days = 15
    author = 'lzc'
    logic = '根据逻辑计算个股 主动新增买单、被动新增买单 不平衡因子 并 衍生分组 主动新增买单、被动新增买单 流动性不平衡因子 相乘'
    article = '中信建投	20201023	因子深度研究系列	买卖报单流动性因子构建'
    freq = '5mins'
    basic_datas = {'daily': ['free_float_shares'], '30mins': [], '5mins': ['activebuyorderamt', 'activebuyordervol', 'activesellorderamt', 'activesellordervol',
                                                                           'passivebuyorderamt', 'passivebuyordervol', 'passivesellorderamt', 'passivesellordervol', 'close'],
                   '1min': []}

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
        activebuyorderamt, activebuyordervol, activesellorderamt, activesellordervol, \
        passivebuyorderamt, passivebuyordervol, passivesellorderamt, passivesellordervol, close = \
            [self.database['5mins'][x] for x in ['activebuyorderamt', 'activebuyordervol', 'activesellorderamt', 'activesellordervol',
                                                 'passivebuyorderamt', 'passivebuyordervol', 'passivesellorderamt', 'passivesellordervol', 'close']]
        free_float_shares = self.database['daily']['free_float_shares']

        activeordervol = activebuyordervol + activesellordervol
        activeorderamt = activebuyorderamt + activesellorderamt

        passiveordervol = passivebuyordervol + passivesellordervol
        passiveorderamt = passivebuyorderamt + passivesellorderamt

        free_float_shares = delay(free_float_shares, 1)
        daily_group = sameshape(free_float_shares, self.group_factor())
        minute_group = sameshape(passiveordervol, self.group_factor())
        IndutryPrice = st2groupst(close * free_float_shares, minute_group,  self.group_func())

        sell_vwap = activeorderamt / activeordervol
        sell_order_amt_group = st2groupst(activeorderamt, minute_group,  self.group_func())
        industry_sell_vwap = sell_order_amt_group / st2groupst(activeordervol, minute_group,  self.group_func())

        VWAPMA_stk = sell_vwap / close - 1
        VWAPMA_group = industry_sell_vwap / IndutryPrice - 1
        MCIA_stk = VWAPMA_stk / activeorderamt
        MCIA_group = VWAPMA_group / sell_order_amt_group
        del activeorderamt, sell_vwap, activeordervol, sell_order_amt_group, VWAPMA_stk, VWAPMA_group
        gc.collect()

        buy_vwap = passiveorderamt / passiveordervol

        buy_order_amt_group = st2groupst(passiveorderamt, minute_group, cross_sum)
        industry_buy_vwap = buy_order_amt_group / st2groupst(passiveordervol, minute_group, cross_sum)
        VWAPMB_stk = buy_vwap / close - 1
        VWAPMB_group = industry_buy_vwap / IndutryPrice - 1
        MCIB_stk = VWAPMB_stk / passiveorderamt
        MCIB_group = VWAPMB_group / buy_order_amt_group
        del buy_order_amt_group, passiveorderamt, buy_vwap, passiveordervol, VWAPMB_stk, VWAPMB_group
        gc.collect()

        MCI_IMB_stk = (MCIB_stk - MCIA_stk) / (MCIB_stk + MCIA_stk)
        MCI_IMB_group = (MCIB_group - MCIA_group) / (MCIB_group + MCIA_group)

        return arr_match_index(MCI_IMB_stk * MCI_IMB_group, self.cal_date_range, self.date_range)

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
    f = IMB_Active_Passive_Price()
    e = time.time()
    # f.result()
    f.result()
    print(f'total calc time {time.time() - e}')
    # send_message(['015664'],f'total calc time {time.time()-e}')
