# coding: utf-8
# Author：fengchi863
# Date ：2021/9/8 20:08

import sys
import os
from ShortTermTrading.TradingPattern.baotuanqushigu.StrategyBackTest.StockStrategyBase import StockStrategyBase
from ShortTermTrading.TradingPattern.baotuanqushigu.StrategyBackTest.UniverseEvaluation import UniverseEvaluation
from xquant.factordata import FactorData
from ShortTermTrading.conf.path_conf import junk_path
import pandas as pd
import numpy as np
import time
from ShortTermTrading.dataApi import stockList, getData
from datetime import datetime
sys.path.append('/data/group/800442/800319/')
sys.path.append('/data/group/800442/800319/Daily_ConCept/')

s = FactorData()


class StockStrategyDemo(StockStrategyBase):

    def __init__(self, stk, start_date, end_date, price_rolling_window=30, amt_per_signal=5000000, available_flag=None,
                 isin_pool_flag=None):
        super().__init__(stk, start_date, end_date, price_rolling_window, amt_per_signal, available_flag,
                         isin_pool_flag)
        if self.market_flow is None:
            return
        self.last_buy_time = None
        self.last_buy_price = None
        self.stock = stk

        self.sell_flag = None
        self.min_factors = None
        self.index_signal = None

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
        self.sell_flag = 0
        return

    def bar_handler(self):
        if self.position['available'] > 0:
            if self.min_factors.at[self.datetime, 'close'] > self.pre_close:
                if self.min_factors.at[self.datetime, 'maxdrawdown'] > 0.035:
                    self.sell()
                    self.sell_flag = 1
        if (self.position['available'] > 0) and (self.datetime[1] > 1450):
            if self.min_factors.at[self.datetime, 'close'] < (
                    np.floor(self.pre_close * 1.1 * 100 + 0.5) / 100 - 0.0001):
                self.sell()
                self.sell_flag = 1
        if self.position['available'] > 0:
            if self.datetime[1] >= 930:
                if self.min_factors.at[self.datetime, 'close'] < (self.pre_close * 0.94):
                    self.sell()
                    self.sell_flag = 1
        if (self.position['available'] > 0) and (self.datetime[1] > 1450):
            if self.min_factors.at[self.datetime, 'close'] < (
                    self.min_factors.at[(self.trading_day, 925), 'close'] * 0.94):
                self.sell()
                self.sell_flag = 1

        if (self.sell_flag == 0) and (self.position['holding'] == 0):
            if (self.datetime[1] >= 930) and (
                    self.min_factors.at[(self.trading_day, 925), 'close'] / self.pre_close >= 0.94):
                if self.min_factors.at[self.datetime, 'high'] > 5:
                    self.buy()
                    self.last_buy_price = self.min_factors.at[self.datetime, 'vwap']


def main():
    # start_date = 20140101
    start_date = 20200101
    end_date = 20201231
    bomb_stock = pd.read_pickle(junk_path + 'zhaban_zt_time_15_20201231.pkl')
    # bomb_stock = pd.read_pickle(junk_path + '叠加板块zhaban_zt_time_15_20211112.pkl')
    # bomb_stock = get_basic_values('Open_Board_stock')
    bomb_stock.index = bomb_stock.index.map(lambda x: int(x))
    bomb_stock.columns = bomb_stock.columns.map(lambda x: stockList.trans_windcode2int(x))
    bomb_stock = (bomb_stock.shift(1).fillna(0)).astype(bool)

    bomb_stk_sum = bomb_stock.sum() > 0
    stk_list = bomb_stk_sum[bomb_stk_sum].index.tolist()
    valid_list = os.listdir('/data/group/800442/800319/junkData/minuteByStock/')
    valid_list = [int(x[:-3]) for x in valid_list]
    stk_list = list(set(stk_list).intersection(set(valid_list)))
    stk_list.sort()
    stk_list = [x for x in stk_list if x // 1000 != 688]
    strats = UniverseEvaluation(StockStrategyDemo, available_info=None, universe_info=bomb_stock)
    e = time.time()
    # 并行回测
    print('炸板股回测开始')
    now = datetime.now().strftime("%Y%m%d%H%M")
    # output_path = junk_path + 'zhaban_bt_result_%s.xlsx' % now
    output_path = junk_path + '叠加板块zhaban_bt_result_%s.xlsx' % now
    strats.one_wave_run(stk_list, start_date, end_date, kernel=20, output_path=output_path, mode='multi')
    print('strategy time:', time.time() - e)
    print(output_path)


if __name__ == "__main__":
    # main_check()
    main()
