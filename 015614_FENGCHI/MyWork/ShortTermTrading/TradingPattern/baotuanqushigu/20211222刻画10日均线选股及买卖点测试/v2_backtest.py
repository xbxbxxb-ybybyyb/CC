# coding: utf-8
# Author：fengchi863
# Date ：2022/1/4 10:18

import os
import sys
import time
import pandas as pd
sys.path.append('/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211222刻画10日均线选股及买卖点测试')

from MyTest.MyOwnStockStrategyBase.StockStrategyBase import StockStrategyBase
from MyTest.MyOwnStockStrategyBase.UniverseEvaluation import UniverseEvaluation
from ShortTermTrading.conf.path_conf import junk_path
from ShortTermTrading.dataApi import getData, tradeDate
import datetime

holding_day = 6


class StockStrategyDemo(StockStrategyBase):
    def __init__(self, stk, start_date, end_date, price_rolling_window=10, amt_per_signal=5000000, available_flag=None,
                 isin_pool_flag=None, **sell_cond_kargs):
        super().__init__(stk, start_date, end_date, price_rolling_window, amt_per_signal, available_flag,
                         isin_pool_flag)
        if self.market_flow is None:
            return

        self.stock = stk
        self.last_buy_time = None
        self.last_cost = 0.1

        self.buy_signal = None
        self.sell_signal = None
        self.sell_cond_kargs = sell_cond_kargs

    def daily_update(self):
        stk_minute = getData.get_minute_1stock(self.stk_id, start_datetime=self.trading_day * 10000 + 925,
                                               end_datetime=self.trading_day * 10000 + 1500,
                                               factor_list=['close', 'vol'])
        stk_adj_factor = getData.get_daily_1stock(self.stk_id, factor_list=['adjfactor'],
                                                  date_list=[self.trading_day]).values[0][0]
        # stk_pre_close = getData.get_daily_1stock(self.stk_id, factor_list=['pre_close_badj'],
        #                                          date_list=[self.trading_day]).values[0][0]
        stk_minute['close_badj'] = stk_minute['close'] * stk_adj_factor

        pre_10d_date_list = tradeDate.get_date_range(tradeDate.get_pre_trade_date(self.trading_day, 10),
                                                    tradeDate.get_pre_trade_date(self.trading_day))
        if self.trading_day == 20210720:
            print(1)
        daily_close_badj = getData.get_daily_1stock(self.stk_id, date_list=pre_10d_date_list, factor_list=['close_badj'])
        ma10_badj = daily_close_badj.mean().values[0]
        ma10_boost_badj = ma10_badj * 1.0
        # [1.005, 1.1]

        expanding_low = stk_minute['close_badj'].expanding().min()

        # 与ma10比较
        ma10_judge = expanding_low < ma10_badj
        # 判断反弹力度
        ma10_up_judge = (stk_minute['close_badj'] / expanding_low - 1) > 0.01
        # [0.005, 0.01, 0.015, 0.02]
        # 判断高于ma10
        ma10_judge2 = stk_minute['close_badj'] > ma10_badj
        all_cond1 = ma10_judge & ma10_up_judge & ma10_judge2

        ma10_judge = expanding_low < ma10_boost_badj
        ma10_judge2 = stk_minute['close_badj'] > ma10_boost_badj
        all_cond2 = ma10_judge & ma10_up_judge & ma10_judge2

        mean_vol = stk_minute['vol'].rolling(20).mean()
        all_cond3 = stk_minute['vol'].rolling(3).mean() > mean_vol

        buy_signal = (all_cond1 | all_cond2) & all_cond3

        # 卖出条件
        # ma5_pct = stk_minute['close_badj'] / ma10_badj - 1
        # ma5_judge3 = (ma5_pct > self.sell_cond_kargs['ma10上方止盈点']) | (ma5_pct < self.sell_cond_kargs['ma10下方止损点'])
        # sell_signal1 = ma5_judge3

        sell_signal1 = stk_minute['close'] / self.last_cost < 0.92

        expanding_high = stk_minute['close_badj'].expanding().max()
        up_pct = expanding_high / ma10_badj > 1.07
        withdraw_pct = stk_minute['close_badj'] / expanding_high < 0.98
        sell_signal2 = up_pct & withdraw_pct

        sell_signal3 = stk_minute['close_badj'] < ma10_badj
        sell_signal3[:1439] = False
        sell_signal3[1441:] = False

        sell_signal = sell_signal1 | sell_signal2 | sell_signal3

        self.buy_signal = buy_signal
        self.sell_signal = sell_signal

    def bar_handler(self):
        buy_signal = self.buy_signal.loc[self.datetime]
        sell_signal = self.sell_signal.loc[self.datetime]
        if buy_signal == 1 and self.position['holding'] == 0:
            self.buy()
            self.last_buy_time = self.datetime[0]
            self.last_cost = self.trade_buy()
        if sell_signal == 1 and self.position['available'] > 0:
            self.sell()
        if tradeDate.get_trade_date_interval(self.trading_day, base_date=self.last_buy_time) == holding_day - 1:
            self.sell()


def start_backtest(start_date, end_date, trend_stock: pd.DataFrame, output_path, mode='multi', **cond_kargs):
    start_date = start_date
    end_date = end_date

    trend_stk_sum = trend_stock.sum() > 0
    stk_list = trend_stk_sum[trend_stk_sum].index.tolist()
    valid_list = os.listdir('/data/group/800442/800319/junkData/minuteByStock/')
    valid_list = list(filter(lambda x: x.endswith('.h5'), valid_list))
    valid_list = [int(x[:-3]) for x in valid_list]
    stk_list = list(set(stk_list).intersection(set(valid_list)))
    stk_list.sort()

    strats = UniverseEvaluation(StockStrategyDemo, available_info=None, universe_info=trend_stock)
    output_path = output_path

    t1 = time.time()
    strats.one_wave_run(stk_list, start_date, end_date, kernel=16, output_path=output_path,
                        append_para=cond_kargs, mode=mode)
    print('strategy time:', time.time() - t1)
