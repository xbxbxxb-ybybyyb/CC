import os
import sys
'''
用来回测一段区间的结果
'''
###这里是回测框架地址
# sys.path.append("/data/user/015630/pycharmproject/StrongStock/")
# sys.path.append("/data/user/015630/pycharmproject/StrongStock/StrongStockModel/")
# from backtest.StrategyBackTest.StockStrategyBase import StockStrategyBase
# from backtest.StrategyBackTest.UniverseEvaluation import UniverseEvaluation
sys.path.append('/data/group/800442/800319/')
sys.path.append('/data/group/800442/800319/Daily_ConCept/')
from ShortTermTrading.ConceptApi import *
from ShortTermTrading.TradingPattern.baotuanqushigu.StrategyBackTest.StockStrategyBase import StockStrategyBase
from ShortTermTrading.TradingPattern.baotuanqushigu.StrategyBackTest.UniverseEvaluation import UniverseEvaluation
from xquant.factordata import FactorData
import pandas as pd
import numpy as np
import time
from ShortTermTrading.dataApi import tradeDate, stockList, dividend, indName, getData
# import talib
from datetime import datetime

s = FactorData()

#pickle_path = '/data/group/800442/800319/Faamonitor/factors/zxf/zhaban/'


class StockStrategyDemo(StockStrategyBase):

    def __init__(self, stk, start_date, end_date, price_rolling_window=10, amt_per_signal=5000000, available_flag=None,
                 isin_pool_flag=None):
        super().__init__(stk, start_date, end_date, price_rolling_window, amt_per_signal, available_flag,
                         isin_pool_flag)
        # self.signal = pd.read_pickle('/data/user/015630/factors/kdj_30/%s.pkl'%stk)
        if self.market_flow is None:
            return
        #self.signal = pd.read_pickle(pickle_path + ('%s.pkl' % stk))
        # self.szzs = getData.get_minute_1stock('SZZZ',start_datetime=201601010930,end_datetime=201912311500,factor_list=['close'],type='bench')
        # signal = pd.read_pickle('/data/group/800319/junkData/IntraFactorModel/predictions/lr_model_rise_down_zero_5min_2018all_mkt_origin_nodrop_factor_20200706/%d.pkl' % stk)
        # if len(signal) == 2:
        #     self.signal = signal[0]
        # else:
        #     self.signal = None
#        tradingdaysstr = s.tradingday(20140101, 20150701)
#        tradingdaysint = [int(x) for x in tradingdaysstr]
        self.last_buy_time = None
        self.last_buy_price = None
        self.stock = stk
        # self.index_data = s.get_factor_value(
        #     "WIND_AIndexEODPrices",
        #     s_info_windcode=['399005.SZ', '399001.SZ', '000001.SH'],
        #     factors=['s_info_windcode', 'trade_dt', 's_dq_close', 's_dq_open', 's_dq_amount'], trade_dt=tradingdaysstr
        # )
        # self.close_index = self.index_data.pivot('TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_CLOSE').loc[tradingdaysstr]
        # self.close_index.index = self.close_index.index.map(int)
        # self.open_index = self.index_data.pivot('TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_OPEN').loc[tradingdaysstr]
        # self.open_index.index = self.open_index.index.map(int)
        # self.ma5_index = self.close_index.rolling(5).mean() < self.close_index
        # self.ma5_sum = self.ma5_index.sum(axis=1)
        # a1, a2, a3 = talib.MACD(np.array(self.close_index['000001.SH']), fastperiod=12, slowperiod=26, signalperiod=9)
        # self.macd = pd.Series(a3, index=tradingdaysint).shift(1)
        # self.open_close = self.open_index < ((self.close_index.shift(1)) * 0.99)
        # self.open_close_sum = self.open_close.sum(axis=1)
        # self.amount = self.index_data.pivot('TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_AMOUNT').loc[tradingdaysstr]
        # self.amount.index = self.amount.index.map(int)
        # self.amount_condition = self.amount > self.amount.shift(1) * 1.02
        # self.amount_condition_sum = self.amount_condition.sum(axis=1)
        # self.share_close = getData.get_daily_1stock(stk, ['close_badj'], tradingdaysint)
        # a1_share, a2_share, a3_share = talib.MACD(np.array(self.share_close['close_badj']), fastperiod=12,
        #                                           slowperiod=26, signalperiod=9)
        # self.macd_share = pd.Series(a3_share, index=tradingdaysint).pct_change().shift(1)

    def daily_update(self):
        self.index_signal = 0
        self.min_factors = getData.get_minute_1stock(self.stock, start_datetime=self.trading_day * 10000 + 925,
                                                     end_datetime=self.trading_day * 10000 + 1500,
                                                     factor_list=['vol', 'amt', 'close', 'low', 'high'])
        self.min_factors['amt_cumsum'] = self.min_factors['amt'].cumsum()
        self.min_factors['vol_cumsum'] = self.min_factors['vol'].cumsum()
        self.min_factors['speed'] = self.min_factors['close'].pct_change(2)
        self.min_factors['liangbi'] = self.min_factors['vol'].rolling(2).sum() / self.min_factors['vol'].rolling(
            10).sum()
        self.min_factors['vwap'] = self.min_factors['amt'] / self.min_factors['vol']
        self.min_factors['yellow_vwap'] = self.min_factors['amt_cumsum'] / self.min_factors['vol_cumsum']
        self.min_factors['close_up_vwap'] = (self.min_factors['close'] / self.min_factors['vwap']) > 1
        self.min_factors['length'] = np.arange(242) + 1
        self.min_factors['close_up_vwap_ratio'] = self.min_factors['close_up_vwap'].cumsum() / self.min_factors[
            'length']
        self.min_factors['maxdrawdown'] = (1 - self.min_factors['close'] / self.min_factors['close'].cummax()).cummax()
        self.min_factors['cummax'] = self.min_factors['high'].cummax()
        self.min_factors['cummin'] = self.min_factors['low'].cummin()
        # if (self.ma5_sum.at[self.preday] >= 2) and (self.macd.at[self.trading_day] > self.macd.at[self.preday]) and (
        #         self.open_close_sum.at[self.trading_day] < 2):
        #     self.index_signal = 1
        self.sell_flag = 0

        return

    def bar_handler(self):
        # 每只股票每分钟信号逻辑定义
        #        if (self.position['available'] > 0) and (self.min_factors.at[(self.trading_day, 925), 'close'] < self.pre_close):
        #            if self.min_factors.at[self.datetime, 'close'] > self.pre_close:
        #                self.sell()
        #                self.sell_flag = 1
        if (self.position['available'] > 0):
            if self.min_factors.at[self.datetime, 'close'] > self.pre_close:
                if self.min_factors.at[self.datetime, 'maxdrawdown'] > 0.035:
                    self.sell()
                    self.sell_flag = 1
        if (self.position['available'] > 0) and (self.datetime[1] > 1450):
            if self.min_factors.at[self.datetime, 'close'] < (
                    np.floor(self.pre_close * 1.1 * 100 + 0.5) / 100 - 0.0001):
                self.sell()
                self.sell_flag = 1
        if (self.position['available'] > 0):
            if self.datetime[1] >= 930:
                if self.min_factors.at[self.datetime, 'close'] < (self.pre_close * 0.94):
                    self.sell()
                    self.sell_flag = 1
        if (self.position['available'] > 0) and (self.datetime[1] > 1450):
            if self.min_factors.at[self.datetime, 'close'] < (
                    self.min_factors.at[(self.trading_day, 925), 'close'] * 0.94):
                self.sell()
                self.sell_flag = 1

        #        if (self.position['available'] > 0):
        #            if self.min_factors.at[self.datetime,'high']/self.last_buy_price>=1.03:
        #                if self.min_factors.at[self.datetime, 'close'] < (np.floor(self.pre_close * 1.1 * 100 + 0.5) / 100 - 0.0001):
        #                    if self.min_factors.at[self.datetime,'speed']<0.01:
        #                        self.sell()
        #                        self.sell_flag = 1
        #                        self.last_buy_price = None

        #        if (self.index_signal == 0) or (self.datetime[1] > 1000):
        #            return
        # if concept in active_concept_list:

        #        if (self.index_signal == 0):
        #            return
        #        if (self.sell_flag == 0) and (self.position['holding'] == 0):
        #            if self.datetime[1]>=930:
        #                self.buy()
        #                self.last_buy_price = self.min_factors.at[self.datetime,'vwap']

        if (self.sell_flag == 0) and (self.position['holding'] == 0):
            if (self.datetime[1] >= 930) and (self.min_factors.at[(self.trading_day,925),'close']/self.pre_close>=0.94):
                if (self.min_factors.at[self.datetime,'high'] > 5):
                    self.buy()
                    self.last_buy_price = self.min_factors.at[self.datetime, 'vwap']


def main2():
    """
    示例2：一波全回测评估并输出
    :return:
    """
    # qiangshigu = pd.read_pickle('/data/group/800319/Faamonitor/HS300.pkl')
    # qiangshigu = pd.read_pickle('/data/group/800319/Faamonitor/zhaban_concept.pkl')
    qiangshigu = pd.read_pickle('/data/group/800442/800319/Faamonitor/zhaban_syx_zt_time_15_20210621.pkl')
    #qiangshigu = get_basic_values('Open_Board_stock')
    qiangshigu.index = qiangshigu.index.map(lambda x: int(x))
    qiangshigu.columns = qiangshigu.columns.map(lambda x: stockList.trans_windcode2int(x))
    qiangshigu = (qiangshigu.shift(1).fillna(0)).astype(bool)
    # qiangshigu = (qiangshigu.fillna(0)).astype(bool)
    #    yaogu = pd.read_pickle('/data/group/800319/Faamonitor/妖股2014-2019.pkl')
    #    yaogu.index = yaogu.index.map(lambda x: int(x))
    #    yaogu.columns = yaogu.columns.map(lambda x: stockList.trans_windcode2int(x))
    #    yaogu = (yaogu.shift(1).fillna(0)).astype(bool)

    is_valid = qiangshigu
    # file_list = os.listdir('/data/user/015630/factors/kdj_30/')
    qiangshigu_sum = qiangshigu.sum()>0
    stk_list = qiangshigu_sum[qiangshigu_sum].index.tolist()
    valid_list = os.listdir('/data/group/800442/800319/junkData/minuteByStock/')
    valid_list = [int(x[:-3]) for x in valid_list]
    stk_list = list(set(stk_list).intersection(set(valid_list)))
    stk_list.sort()
    # stk_list_str = [stockList.trans_int2windcode(x) for x in stk_list]
    stk_list = [x for x in stk_list if x // 1000 != 688]
    strats = UniverseEvaluation(StockStrategyDemo, available_info=None, universe_info=is_valid)
    # strats.backtest_one_stock(1, 20130101, 20191231)
    e = time.time()
    # 并行回测
    print('强势股回测开始')
    now = datetime.now().strftime("%Y%m%d%H%M")
    # output_path = '/data/group/800319/Faamonitor/ruozhuanqiang_type3_add_sell_condition_%s.xlsx'%now
    output_path = '/data/group/800442/800319/Faamonitor/zhaban%s.xlsx' % now
    strats.one_wave_run(stk_list, 20210621, 20210713, kernel=20, output_path=output_path, mode='multi')

    print('strategy time:', time.time() - e)
    print(output_path)


if __name__ == "__main__":
    # main_check()
    main2()
