# coding: utf-8
# Author：fengchi863
# Date ：2020/10/13 10:43

import os
import sys

sys.path.append("/data/user/015614/MyWork/")
sys.path.append("/data/user/015614/MyWork/StrongStockModel/")
sys.path.append('/data/group/800319')
from backtest.StrategyBackTest.StockStrategyBase import StockStrategyBase
import pandas as pd
import time
from backtest.StrategyBackTest.UniverseEvaluation import UniverseEvaluation
from dataApi import stockList, getData

start_date = 20140101
end_date = 20161231

run_date = 20201026
run_datetime = 202010281540

pattern_name = '大盘逆势上涨'
holding_day = 1

root_path = '/data/group/800319/fengchi/pattern_test/'
pickle_path = root_path + '/%s/%s/个股_%d_%d/' % (pattern_name, run_date, start_date, end_date)

stk_df_path = '/data/group/800319/fengchi/pattern_test/%s/%s/外部股票池_%d_%d/stk_df.pkl' % (
    pattern_name, run_date, start_date, end_date)

output_path = root_path + '%s/%s/结果_%d_%d_%d/回测结果_%d_%d_%d_%d.xlsx' % (
    pattern_name, run_date, start_date, end_date, run_datetime, holding_day, start_date, end_date, run_datetime)

if not os.path.exists(
        '/data/group/800319/fengchi/pattern_test/%s/%s/结果_%d_%d_%d/' % (
                pattern_name, run_date, start_date, end_date, run_datetime)):
    os.makedirs(
        '/data/group/800319/fengchi/pattern_test/%s/%s/结果_%d_%d_%d/' % (
            pattern_name, run_date, start_date, end_date, run_datetime))


class StockStrategyDemo(StockStrategyBase):

    def __init__(self, stk, start_date, end_date, price_rolling_window=10, amt_per_signal=5000000, available_flag=None,
                 isin_pool_flag=None):
        super().__init__(stk, start_date, end_date, price_rolling_window, amt_per_signal, available_flag,
                         isin_pool_flag)
        if self.market_flow is None:
            return
        self.signal = pd.read_pickle(pickle_path + ('%s.pkl' % stk)).loc[self.date_list]
        self.stock = stk
        self.last_buy_time = None

    def daily_update(self):
        # 每天基类会更新行情数据，此函数用于每天额外更新策略中需要使用的数据，如没有额外需要使用的数据，可不定义该函数
        # 每天额外更新数据
        self.stk_minute = getData.get_minute_1stock(self.stk_id, start_datetime=self.trading_day * 10000 + 930, \
                                                    end_datetime=self.trading_day * 10000 + 1500,
                                                    factor_list=['close', 'amt'])
        self.stk_adj_factor = getData.get_daily_1stock(self.stk_id, factor_list=['adjfactor'], \
                                                       date_list=[self.trading_day]).values[0][0]
        self.stk_pre_close = getData.get_daily_1stock(self.stk_id, factor_list=['pre_close_badj'], \
                                                      date_list=[self.trading_day]).values[0][0]
        self.stk_minute['close_badj'] = self.stk_minute['close'] * self.stk_adj_factor
        self.stk_pctchg = self.stk_minute['close_badj'] / self.stk_pre_close - 1

        self.pctchg_speed_1m = self.stk_minute['close_badj'].pct_change(1)
        self.pctchg_speed_2m = self.stk_minute['close_badj'].pct_change(2)
        self.pctchg_speed_3m = self.stk_minute['close_badj'].pct_change(3)
        self.pctchg_speed_4m = self.stk_minute['close_badj'].pct_change(4)
        self.pctchg_speed_5m = self.stk_minute['close_badj'].pct_change(5)

        self.stk_amt_rolling10 = self.stk_minute['amt'].shift(1).rolling(10).mean()
        self.stk_amt_rolling_1m_mean = self.stk_minute['amt'].shift(1).rolling(1).mean()
        self.stk_amt_rolling_2m_mean = self.stk_minute['amt'].shift(1).rolling(2).mean()
        self.stk_amt_rolling_3m_mean = self.stk_minute['amt'].shift(1).rolling(3).mean()
        self.stk_amt_rolling_4m_mean = self.stk_minute['amt'].shift(1).rolling(4).mean()
        self.stk_amt_rolling_5m_mean = self.stk_minute['amt'].shift(1).rolling(5).mean()
        return

    def bar_handler(self):
        # 每只股票每分钟信号逻辑定义
        if self.signal is None:
            return
        if not self.datetime in self.signal.index:
            return

        signal = self.signal.at[self.datetime, 'prediction']
        if signal == 1 and self.position['holding'] == 0:
            # 买入函数可输入具体买入手数，该参数默认为 None, 如不输入，则默认买入self.amt_per_signal/均价 （四舍五入到手）
            sort_dict = {1: self.pctchg_speed_1m.loc[self.datetime[0], self.datetime[1]],
                         2: self.pctchg_speed_2m.loc[self.datetime[0], self.datetime[1]],
                         3: self.pctchg_speed_3m.loc[self.datetime[0], self.datetime[1]],
                         4: self.pctchg_speed_4m.loc[self.datetime[0], self.datetime[1]],
                         5: self.pctchg_speed_5m.loc[self.datetime[0], self.datetime[1]]}
            sort_dict = sorted(sort_dict.items(), key=lambda x: x[1], reverse=True)
            if sort_dict[0][1] > 0.02:
                if self.datetime[1] < 940:
                    self.buy()
                    self.last_buy_time = self.datetime[0]
                    return
                max_up_minute_window = sort_dict[0][0]
                if max_up_minute_window == 1:
                    if (self.stk_amt_rolling_1m_mean / self.stk_amt_rolling10).loc[
                        self.datetime[0], self.datetime[1]] < 0.8:
                        return
                if max_up_minute_window == 2:
                    if (self.stk_amt_rolling_2m_mean / self.stk_amt_rolling10).loc[
                        self.datetime[0], self.datetime[1]] < 0.8:
                        return
                if max_up_minute_window == 3:
                    if (self.stk_amt_rolling_3m_mean / self.stk_amt_rolling10).loc[
                        self.datetime[0], self.datetime[1]] < 0.8:
                        return
                if max_up_minute_window == 4:
                    if (self.stk_amt_rolling_4m_mean / self.stk_amt_rolling10).loc[
                        self.datetime[0], self.datetime[1]] < 0.8:
                        return
                if max_up_minute_window == 5:
                    if (self.stk_amt_rolling_5m_mean / self.stk_amt_rolling10).loc[
                        self.datetime[0], self.datetime[1]] < 0.8:
                        return
            else:
                return
            self.buy()
            self.last_buy_time = self.datetime[0]
        if self.position['available'] > 0 and \
                getData.get_trade_date_interval(self.trading_day, base_date=self.last_buy_time) >= (holding_day - 1):
            # 卖出函数可输入具体卖出手数，该参数默认为None, 如不输入，则默认卖出所有持仓
            if self.datetime[1] < 1455 and self.stk_pctchg.loc[self.datetime[0], self.datetime[1]] > 0.07:  # 止盈条件
                self.sell()
            if self.datetime[1] == 1455:
                self.sell()


def main2():
    """
    示例2：一波全回测评估并输出
    :return:
    """
    qiangshigu = pd.read_pickle(stk_df_path)
    qiangshigu.index = qiangshigu.index.map(lambda x: int(x))
    qiangshigu.columns = qiangshigu.columns.map(lambda x: stockList.trans_windcode2int(x))
    qiangshigu = (qiangshigu.fillna(0)).astype(bool)

    is_valid = qiangshigu
    file_list = os.listdir(pickle_path)
    file_list = list(filter(lambda x: 'Wrong' not in x, file_list))
    stk_list = [int(x.strip('.pkl')) for x in file_list]

    strats = UniverseEvaluation(StockStrategyDemo, buy_cost_ratio=0.001, sell_cost_ratio=0.001, available_info=None,
                                universe_info=is_valid)
    # strats.backtest_one_stock(1, 20130101, 20191231)
    e = time.time()
    # 并行回测
    print('强势股回测开始')

    strats.one_wave_run(stk_list, start_date, end_date, kernel=24, output_path=output_path, mode='serial')
    # record = pd.read_pickle('/data/group/800319/Faamonitor/temp_record/kdj_record_for_test_by_lzc.pkl')
    # os.mkdir('/data/group/800319/Faamonitor/temp_record/')
    # pd.to_pickle(strats.record._getvalue(),'/data/group/800319/Faamonitor/temp_record/kdj_record_for_test_by_lzc.pkl')
    # for k in record:
    #     strats.record[k] = record[k]
    # _ = strats.evaluate_by_signal()
    #    print('妖股回测开始')
    #    is_valid = yaogu
    #    strats = UniverseEvaluation(StockStrategyDemo, available_info=None, universe_info=is_valid)
    #    output_path = '/data/group/800319/Faamonitor/factors/factors_result/yaogu_keltner30_result.xlsx'
    #    strats.one_wave_run(stk_list, 20140101, 20181231, kernel=24, output_path=output_path, mode='multi')
    # pd.to_pickle(strats.record._getvalue(), '/data/group/800319/Faamonitor/factors/record_zxf_code_excute_by_lzc.pkl')
    # strats.one_wave_run(stk_list, 20100101, 20200728, kernel=10, output_path='/data/group/800319/Faamonitor/kdj_result_multi.xlsx', mode='multi')
    print('strategy time:', time.time() - e)


if __name__ == "__main__":
    # main_check()
    main2()