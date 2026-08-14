# @Time : 2020/9/4 10:14
# @Author : Zhichen Lu
# @File : TrueLabelTest.py

import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
from backtest.StrategyBackTest.StockStrategyBase import StockStrategyBase
import pandas as pd
import time
from backtest.StrategyBackTest.UniverseEvaluation import UniverseEvaluation
from dataApi import tradeDate, stockList, dividend, indName, getData
from StrongStockModel.conf.path_config import root_path
from multiprocessing import Manager
import itertools

signal = pd.read_pickle(root_path + 'model_signal/True_Label_2pct.pkl')
signal_global = Manager().dict(signal)

class StockStrategyBySignal(StockStrategyBase):

    def __init__(self, stk, start_date, end_date, price_rolling_window=10, amt_per_signal=5000000, available_flag=None,
                 isin_pool_flag=None):
        super().__init__(stk, start_date, end_date, price_rolling_window, amt_per_signal, available_flag,
                         isin_pool_flag)
        if stk in signal_global:
            self.signal = pd.DataFrame(signal_global[stk])
        else:
            self.signal = None
            self.market_flow = None
        self.stock = stk
        target_index = pd.MultiIndex.from_tuples(list(itertools.product(self.date_list, [1000, 1030, 1100, 1300, 1330, 1400, 1430])))
        self.signal = self.signal.reindex(target_index)
        self.last_buy_datetime = None
        self.over_24h = False

    def daily_update(self):
        # 每天基类会更新行情数据，此函数用于每天额外更新策略中需要使用的数据，如没有额外需要使用的数据，可不定义该函数
        # 每天额外更新数据
        if self.trading_day in self.signal.index:
            self.dataflow['signal'] = self.signal[self.i * 7:self.i * 7 + 7]
        else:
            self.dataflow['signal'] = None

    def bar_handler(self):
        # 每只股票每分钟信号逻辑定义
        if self.datetime==(20141216,1000):
            print(1)
        if self.dataflow['signal'] is None:
            return
        # self.datetime (20170103,930)
        if not self.datetime in self.dataflow['signal'].index:
            return

        signal = self.dataflow['signal'].at[self.datetime, self.stk_id]
        if signal == 1 and self.position['holding'] == 0:
            # 买入函数可输入具体买入手数，该参数默认为 None, 如不输入，则默认买入self.amt_per_signal/均价 （四舍五入到手）
            self.buy()
            self.last_buy_datetime = self.datetime + (self.i,)
        if signal != 1 and self.position['available'] > 0:
            # 卖出函数可输入具体卖出手数，该参数默认为None, 如不输入，则默认卖出所有持仓
            if self.last_buy_datetime is None:
                raise Exception('Wrong situation')
            holding_days = self.i - self.last_buy_datetime[-1]
            if holding_days > 1 or (holding_days == 1 and self.last_buy_datetime[1]>=self.datetime[1]):
                self.sell()
                self.last_buy_datetime = None


def main():
    """
    示例2：一波全回测评估并输出
    :return:
    """
    strong_stock = pd.read_pickle('/data/group/800319/Faamonitor/强势个股2014-2019.pkl')
    strong_stock.index = strong_stock.index.map(lambda x: int(x))
    strong_stock.columns = strong_stock.columns.map(lambda x: stockList.trans_windcode2int(x))
    strong_stock = (strong_stock.shift(1).fillna(0)).astype(bool)

    is_valid = strong_stock

    stk_list = list(signal.keys())

    strats = UniverseEvaluation(StockStrategyBySignal, available_info=None, universe_info=is_valid)
    # strats.backtest_one_stock(2989, 20130101, 20191231)
    e = time.time()
    # 并行回测
    output_path = '/data/group/800319/Faamonitor/factors/True_Label_BackTest_2pct.xlsx'
    strats.one_wave_run([1], 20140103, 20181231, kernel=10, output_path=output_path, mode='serial')
    # pd.to_pickle(strats.record._getvalue(), '/data/group/800319/Faamonitor/factors/record_zxf_code_excute_by_lzc.pkl')
    # strats.one_wave_run(stk_list, 20100101, 20200728, kernel=10, output_path='/data/group/800319/Faamonitor/kdj_result_multi.xlsx', mode='multi')
    print('strategy time:', time.time() - e)
    print(output_path)


if __name__ == "__main__":
    # main_check()
    main()
