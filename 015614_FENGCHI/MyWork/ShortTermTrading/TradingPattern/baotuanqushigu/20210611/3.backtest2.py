# coding: utf-8
# Author：fengchi863
# Date ：2021/6/11 15:39

# coding: utf-8
# Author：zhangxufan
# Date ：2020/7/29 9:30

# @Time : 2020/7/17 10:25
# @Author : Zhichen Lu
# @File : StockStrategyDemo.py

from ShortTermTrading.TradingPattern.baotuanqushigu.StrategyBackTest.StockStrategyBase import StockStrategyBase
from ShortTermTrading.TradingPattern.baotuanqushigu.StrategyBackTest.UniverseEvaluation import UniverseEvaluation
# from StrongStockModel.backtest.StrategyBackTest.StockStrategyBase import StockStrategyBase
# from StrongStockModel.backtest.StrategyBackTest.UniverseEvaluation import UniverseEvaluation
import pandas as pd
import time
import os
from ShortTermTrading.conf.path_conf import junk_path

class StockStrategyDemo(StockStrategyBase):

    def __init__(self, stk, start_date, end_date, price_rolling_window = 10, amt_per_signal = 5000000, available_flag = None,
                 isin_pool_flag=None):
        super().__init__(stk, start_date, end_date, price_rolling_window, amt_per_signal, available_flag, isin_pool_flag)
        if self.market_flow is None:
            return
        self.signal = pd.read_pickle(junk_path + '20210616/%d.pkl' % stk)

        if self.signal is None:
            return

        if self.signal['prediction'].sum() > 0:
            print(stk, self.signal['prediction'].sum())
        self.stock = stk
        self.last_buy_time = None

    def daily_update(self):
        pass

    def bar_handler(self):
        if not self.datetime in self.signal.index:
            return

        signal = self.signal.at[self.datetime, 'prediction']
        if signal == 1 and self.position['holding'] == 0:
            self.buy()
            self.last_buy_time = self.datetime[0]
        if self.position['available'] > 0:
            if self.datetime[1] >= 930:
                self.sell()


def main():
    file_list = os.listdir('/data/user/015630/factors/kdj/')
    file_list = list(filter(lambda x: 'Wrong' not in x, file_list))
    stk_list = [int(x.strip('.pickle')) for x in file_list]
    strats = UniverseEvaluation(StockStrategyDemo)
    e = time.time()
    # 并行回测
    strats.multi_run(stk_list[:30],20100101,20200728,kernel=10)
    print('strategy time:',time.time()-e)
    # 按信号评估
    res_all, record_mean = strats.evaluate_by_signal()
    # 按日评估
    daily_res = strats.evaluate_daily()

def main2():
    """
    示例2：一波全回测评估并输出
    :return:
    """
    path = junk_path + '20210616/'
    file_list = os.listdir(path)
    file_list = list(filter(lambda x: 'Wrong' not in x, file_list))
    stk_list = [int(x.strip('.pkl')) for x in file_list]

    is_valid = pd.read_pickle(junk_path + '20210616_daily_stock_flag.pkl')

    strats = UniverseEvaluation(StockStrategyDemo, available_info=None, universe_info=is_valid)
    # strats.backtest_one_stock(2697,20170704,20181231)
    e = time.time()
    # 并行回测
    strats.one_wave_run(stk_list, 20140101, 20201231, kernel=16, output_path=junk_path+'20210616_bt_result.xlsx', mode='multi')
    print('strategy time:',time.time()-e)

if __name__ == "__main__":
    main2()
