# coding: utf-8
# Author：fengchi863
# Date ：2022/5/16 17:24

import pandas as pd
import time
import os
from SimiStock.SimiBackTest.StrategeBackTestBase import StrategyBackTestBase
from SimiStock.SimiBackTest.StrategyEvaluation import StrategyEvaluation
from ShortTermTrading.conf.path_conf import junk_path
from SimiStock.dataApi import stockList, getData, tradeDate

holding_day = 3


class StockStrategyImpl2Base(StrategyBackTestBase):
    def __init__(self, stk_id, start_date, end_date, price_rolling_window=10, amt_per_signal=5000000,
                 available_flag=None, isin_pool_flag=None):
        super().__init__(stk_id, start_date, end_date, price_rolling_window, amt_per_signal, available_flag, isin_pool_flag)

        self.stock = stk_id
        self.last_buy_time = None

        self.buy_signal = None
        self.sell_signal = None

    def daily_update(self):
        stk_minute = getData.get_minute_1stock(self.stk_id, start_datetime=self.trade_date * 10000 + 925,
                                               end_datetime=self.trade_date * 10000 + 1500,
                                               factor_list=['close'])
        stk_adj_factor = getData.get_daily_1stock(self.stk_id, factor_list=['adjfactor'],
                                                  date_list=[self.trade_date]).values[0][0]
        stk_pre_close = getData.get_daily_1stock(self.stk_id, factor_list=['pre_close_badj'],
                                                 date_list=[self.trade_date]).values[0][0]
        stk_minute['close_badj'] = stk_minute['close'] * stk_adj_factor

        pre_5d_date_list = tradeDate.get_date_range(tradeDate.get_pre_trade_date(self.trade_date, 5),
                                                    tradeDate.get_pre_trade_date(self.trade_date))
        daily_close_badj = getData.get_daily_1stock(self.stk_id, date_list=pre_5d_date_list, factor_list=['close_badj'])
        ma5_badj = daily_close_badj.mean().values[0]
        ma5_boost_badj = ma5_badj * 1.005  # 参数一枚

        expanding_low = stk_minute['close_badj'].expanding().min()
        # 与昨收价比较
        expanding_low_pct = expanding_low / stk_pre_close - 1
        expanding_low_pct_judge = expanding_low_pct < -0.01
        # 与ma5比较
        ma5_judge = expanding_low < ma5_badj
        # 判断反弹力度
        ma5_up_judge = (stk_minute['close_badj'] / expanding_low - 1) > 0.01
        # 判断高于ma5
        ma5_judge2 = stk_minute['close_badj'] > ma5_badj
        all_cond1 = expanding_low_pct_judge & ma5_judge & ma5_up_judge & ma5_judge2

        ma5_judge = expanding_low * stk_adj_factor < ma5_boost_badj
        ma5_judge2 = stk_minute['close_badj'] > ma5_boost_badj
        all_cond2 = expanding_low_pct_judge & ma5_judge & ma5_up_judge & ma5_judge2

        buy_signal = all_cond1 | all_cond2

        # 卖出条件
        ma5_pct = stk_minute['close_badj'] / ma5_badj - 1
        ma5_judge3 = (ma5_pct > 0.05) | (ma5_pct < -0.04)  # 依靠ma5设置止盈点和止损点
        sell_signal = ma5_judge3

        self.buy_signal = buy_signal
        self.sell_signal = sell_signal

    def bar_handler(self):
        buy_signal = self.buy_signal.loc[self.datetime]
        sell_signal = self.sell_signal.loc[self.datetime]
        if buy_signal == 1 and self.position['holding'] == 0:
            self.buy_action()
            self.last_buy_time = self.datetime[0]
        if sell_signal == 1 and self.position['available'] > 0:
            self.sell_action()
        if tradeDate.get_trade_date_interval(self.trade_date, base_date=self.last_buy_time) == holding_day - 1:
            self.sell_action()


if __name__ == '__main__':
    start_date = 20200101
    end_date = 20211201
    bomb_stk = pd.read_pickle(junk_path + 'trend_daily_stock_20211208_mkt0.pkl')
    bomb_stk_sum = bomb_stk.sum() > 0

    stk_list = bomb_stk_sum[bomb_stk_sum].index.tolist()

    valid_list = os.listdir('/data/group/800442/800319/junkData/minuteByStock/')
    valid_list = list(filter(lambda x: x.endswith('.h5'), valid_list))
    valid_list = [int(x[:-3]) for x in valid_list]
    stk_list = list(set(stk_list).intersection(set(valid_list)))
    stk_list.sort()

    strats = StrategyEvaluation(StockStrategyImpl2Base, universe_info=bomb_stk)
    strats.start_backtest(stk_list, start_date, end_date, kernel=10, filename='回测框架验证.xlsx')
    # strats.backtest_1stock(9, 20200101, 20211201)
    e = time.time()
    # strats.serial_run(stk_list[:30], 20200101, 20211201)
    strats.multi_run(stk_list[:30], 20200101, 20211201)
    print('strategy time:', time.time()-e)
    # strats.evaluate_signal_by_stk(9)
    # strats.evaluate_stk_by_day(9)
    # a, b = strats.evaluate_by_signal(kernal=1)
    # abc = strats.evaluate_daily(1)