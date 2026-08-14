# @Time : 2020/7/17 10:25
# @Author : Zhichen Lu
# @File : StockStrategyDemo.py

from backtest.StrategyBackTest.StockStrategyBase import StockStrategyBase
import pandas as pd
import time
from backtest.StrategyBackTest.UniverseEvaluation import UniverseEvaluation
import os

class StockStrategyDemo(StockStrategyBase):

    def __init__(self, stk, start_date, end_date, price_rolling_window = 10,amt_per_signal = 5000000,available_flag = None):
        super().__init__(stk, start_date, end_date, price_rolling_window,amt_per_signal,available_flag)
        signal = pd.read_pickle('/data/group/800319/junkData/IntraFactorModel/predictions/lr_model_rise_down_zero_5min_2018all_mkt_origin_nodrop_factor_20200706/%d.pkl' % stk)
        self.signal = signal
        # if len(signal) == 2:
        #     self.signal = signal[0]
        # else:
        #     self.signal = None

    def daily_update(self):
        # 每天基类会更新行情数据，此函数用于每天额外更新策略中需要使用的数据，如没有额外需要使用的数据，可不定义该函数
        # 每天额外更新数据
        if (self.trading_day, 1000) in self.signal.index:
            self.dataflow['signal'] = self.signal.loc[(self.trading_day, 925):(self.trading_day, 1500)].reindex(self.dataflow['market'].index.tolist())
        else:
            self.dataflow['signal'] = None

    def bar_handler(self):
        # 每只股票每分钟信号逻辑定义
        if self.dataflow['signal'] is None:
            return
        signal = self.dataflow['signal'].loc[self.datetime,'prediction']
        if signal == 1 and self.position['holding']==0:
            # 买入函数可输入具体买入手数，该参数默认为 None, 如不输入，则默认买入self.amt_per_signal/均价 （四舍五入到手）
            self.buy()
        if signal == -1 and self.position['available']>0:
            # 卖出函数可输入具体卖出手数，该参数默认为None, 如不输入，则默认卖出所有持仓
            self.sell()

def main():
    """
    示例1： 逐个调用内部函数
    :return:
    """
    file_list = os.listdir('/data/group/800319/junkData/IntraFactorModel/predictions/lr_model_rise_down_zero_5min_2018all_mkt_origin_nodrop_factor_20200706/')
    file_list = list(filter(lambda x: 'Wrong' not in x, file_list))
    stk_list = [int(x.strip('.pkl')) for x in file_list]
    strats = UniverseEvaluation(StockStrategyDemo)
    # strats.backtest_one_stock(2697,20170704,20181231)
    e = time.time()
    # 并行回测
    strats.multi_run(stk_list[:30],20170704,20181231,kernel=10)
    print('strategy time:',time.time()-e)
    # 按信号评估
    res_all,record_mean = strats.evaluate_by_signal()
    # 按日评估
    daily_res = strats.evaluate_daily()

def main2():
    """
    示例2：一波全回测评估并输出
    :return:
    """
    file_list = os.listdir('/data/group/800319/junkData/IntraFactorModel/predictions/lr_model_rise_down_zero_5min_2018all_mkt_origin_nodrop_factor_20200706/')
    file_list = list(filter(lambda x: 'Wrong' not in x, file_list))
    stk_list = [int(x.strip('.pkl')) for x in file_list]
    strats = UniverseEvaluation(StockStrategyDemo)
    # strats.backtest_one_stock(2697,20170704,20181231)
    e = time.time()
    # 并行回测
    strats.one_wave_run(stk_list, 20170704, 20181231,kernel=10, output_path='/data/group/800319/junkData/IntraFactorModel/predictions/TplusNDemoResult.xlsx')
    print('strategy time:',time.time()-e)


if __name__ == "__main__":
    main2()
