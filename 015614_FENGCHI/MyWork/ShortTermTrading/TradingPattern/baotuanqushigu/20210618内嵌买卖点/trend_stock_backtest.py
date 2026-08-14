# coding: utf-8
# Author：fengchi863
# Date ：2021/6/18 15:39

import os
import time

import pandas as pd

from ShortTermTrading.TradingPattern.baotuanqushigu.StrategyBackTest.StockStrategyBase import StockStrategyBase
from ShortTermTrading.TradingPattern.baotuanqushigu.StrategyBackTest.UniverseEvaluation import UniverseEvaluation
from ShortTermTrading.conf.path_conf import junk_path
from ShortTermTrading.dataApi import getData, tradeDate

holding_day = 3

class StockStrategyDemo(StockStrategyBase):

    def __init__(self, stk, start_date, end_date, price_rolling_window = 10, amt_per_signal = 5000000, available_flag = None,
                 isin_pool_flag=None):
        super().__init__(stk, start_date, end_date, price_rolling_window, amt_per_signal, available_flag, isin_pool_flag)
        if self.market_flow is None:
            return

        self.stock = stk
        self.last_buy_time = None

        self.buy_signal = None
        self.sell_signal = None

    def daily_update(self):
        stk_minute = getData.get_minute_1stock(self.stk_id, start_datetime=self.trading_day * 10000 + 925,
                                                    end_datetime=self.trading_day * 10000 + 1500,
                                                    factor_list=['close'])
        stk_adj_factor = getData.get_daily_1stock(self.stk_id, factor_list=['adjfactor'],
                                                       date_list=[self.trading_day]).values[0][0]
        stk_pre_close = getData.get_daily_1stock(self.stk_id, factor_list=['pre_close_badj'],
                                                      date_list=[self.trading_day]).values[0][0]
        stk_minute['close_badj'] = stk_minute['close'] * stk_adj_factor

        pre_5d_date_list = tradeDate.get_date_range(tradeDate.get_pre_trade_date(self.trading_day, 5), tradeDate.get_pre_trade_date(self.trading_day))
        daily_close_badj = getData.get_daily_1stock(self.stk_id, date_list=pre_5d_date_list, factor_list=['close_badj'])
        ma5_badj = daily_close_badj.mean().values[0]
        ma5_boost_badj = ma5_badj * 1.005 # 参数一枚

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

        ### 卖出条件
        ma5_pct = stk_minute['close_badj'] / ma5_badj - 1
        ma5_judge3 = (ma5_pct > 0.05) | (ma5_pct < -0.05)  # 依靠ma5设置止盈点和止损点
        sell_signal = ma5_judge3

        self.buy_signal = buy_signal
        self.sell_signal = sell_signal

    def bar_handler(self):
        buy_signal = self.buy_signal.loc[self.datetime]
        sell_signal = self.sell_signal.loc[self.datetime]
        if buy_signal == 1 and self.position['holding'] == 0:
            self.buy()
            self.last_buy_time = self.datetime[0]
        if sell_signal == 1 and self.position['available'] > 0:
            self.sell()
        if tradeDate.get_trade_date_interval(self.trading_day, base_date=self.last_buy_time) == holding_day - 1:
            self.sell()


def main():
    file_list = os.listdir('/data/user/015630/factors/kdj/')
    file_list = list(filter(lambda x: 'Wrong' not in x, file_list))
    stk_list = [int(x.strip('.pickle')) for x in file_list]
    strats = UniverseEvaluation(StockStrategyDemo)
    e = time.time()
    # 并行回测
    strats.multi_run(stk_list[:30], 20100101, 20200728, kernel=10)
    print('strategy time:', time.time() - e)
    # 按信号评估
    res_all, record_mean = strats.evaluate_by_signal()
    # 按日评估
    daily_res = strats.evaluate_daily()

def main2():
    path = junk_path + '20210616/'
    file_list = os.listdir(path)
    file_list = list(filter(lambda x: 'Wrong' not in x, file_list))
    stk_list = [int(x.strip('.pkl')) for x in file_list]

    is_valid = pd.read_pickle(junk_path + '20210616_daily_stock_flag.pkl')

    strats = UniverseEvaluation(StockStrategyDemo, available_info=None, universe_info=is_valid)
    # strats.backtest_one_stock(1, 20171123, 20180927) # 调试单指个股
    e = time.time()
    # 并行回测
    strats.one_wave_run(stk_list, 20140101, 20201231, kernel=16, output_path=junk_path+'20210616_bt_result_buysellConsider.xlsx', mode='multi')
    print('strategy time:',time.time()-e)


if __name__ == "__main__":
    main2()
